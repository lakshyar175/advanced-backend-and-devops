from sqlalchemy import Integer, String, Column, create_engine, DateTime
from sqlalchemy.orm import Session, declarative_base
from datetime import datetime, timezone, timedelta
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

DB_PATH = "election.db"
engine = create_engine(f"sqlite:///{DB_PATH}")
Base = declarative_base()

POSITIONS = ["class_rep","sports_secretary","cultural_secretary","tech_secretary"]

# USERNAME = "Lucky"
# PASSWORD = "0123"

ACCESS_TOKEN_EXPIRY = 15
REFRESH_TOKEN_EXPIRY = 7 * 24 * 60
SECRET_KEY = "secret1234"
ALGORITHM = "HS256"

ph = PasswordHasher()

class Candidates(Base):
    __tablename__ = "candidates"
    id = Column(Integer, primary_key=True)
    roll_no = Column(String)
    name = Column(String)
    position = Column(String)
    manifesto = Column(String)
    status = Column(String, default="nominated")
    nominated_on = Column(DateTime, default=datetime.now)

class Votes(Base):
    __tablename__ = "votes"
    id = Column(Integer, primary_key=True)
    position = Column(String)
    candidate_id = Column(Integer)
    voter_roll = Column(String)
    voted_on = Column("voted_on", DateTime, default=datetime.now)


class Election(Base):
    __tablename__ = "election"
    id = Column(Integer, primary_key=True)
    phase = Column(String, default="nominations")


class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    user_name = Column(String, unique=True)
    roll_no = Column(String, unique=True, nullable=True)
    password = Column(String)
    user_type = Column(String, default="student")    

Base.metadata.create_all(engine)

def verify_login(username, password):
    session = Session(engine)
    user = session.query(Users).filter_by(user_name=username).first()
    if user is None:
        session.close()
        return False
    try:
        ph.verify(user.password, password)
    except VerifyMismatchError:
        session.close()
        return False
    user_type = user.user_type
    session.close()
    access_token = create_token(username=username, token_type="access", user_type=user_type)
    refresh_token = create_token(username=username, token_type="refresh", user_type=user_type)
    return {"access_token": access_token, "refresh_token": refresh_token}

def create_token(username, token_type, user_type="student"):
    time = ACCESS_TOKEN_EXPIRY
    if token_type == "refresh":
        time = REFRESH_TOKEN_EXPIRY
    payload = {"username": username, "token_type": token_type, "exp": datetime.now(timezone.utc) + timedelta(minutes=time), "user_type": user_type}

    token = jwt.encode(payload=payload, key=SECRET_KEY, algorithm=ALGORITHM)
    return token 

def verify_token(token, token_type):
    try:
     payload = jwt.decode(jwt=token, key=SECRET_KEY, algorithms=[ALGORITHM])
    except:
        return False
    if payload["token_type"] == token_type:
        return payload["username"]
    return False

def get_user_type(username):
    session = Session(engine)
    user = session.query(Users).filter_by(user_name=username).first()
    if user is None:
        session.close()
        return False
    user_type = user.user_type
    session.close()
    return user_type


def initialize_database():
    session = Session(engine)
    election = session.query(Election).first()
    if election is None:
        election = Election(id=1, phase="nominations")
        session.add(election)
        session.commit()
    session.close()

def register_user(user_name, password, user_type="student"):
    session = Session(engine)
    existing_user = session.query(Users).filter(Users.user_name == user_name).first()
    if existing_user is not None:
        session.close()
        return False
    hashed_password = ph.hash(password)
    user = Users(user_name=user_name, password=hashed_password, user_type=user_type)
    session.add(user)
    session.commit()
    session.close()
    return True


# E1
def get_all_candidates(position=None, approved_only=False):
    session = Session(engine)
    candidates = session.query(Candidates)
    if position is not None:
        candidates = candidates.filter(Candidates.position == position)
    if approved_only:
        candidates = candidates.filter(Candidates.status == "approved")
    result = candidates.all()
    session.close()
    return result


# E2
def get_candidate(candidate_id):
    session = Session(engine)
    candidate = session.get(Candidates, candidate_id)
    session.close()
    if candidate is None:
        return "not_found"
    return candidate


# E3
def add_candidate(roll_no, name, position, manifesto):
    session = Session(engine)
    if position not in POSITIONS:
        session.close()
        return "invalid_position"
    existing = session.query(Candidates).filter(Candidates.roll_no == roll_no,Candidates.status != "withdrawn").first()
    
    if existing is not None:
        session.close()
        return "duplicate_roll"
    candidate = Candidates(roll_no=roll_no,name=name,position=position,manifesto=manifesto,status="nominated")
    session.add(candidate)
    session.commit()
    session.close()
    return "nominated"

#  E4
def approve_candidate(candidate_id):
    session = Session(engine)
    election = session.query(Election).first()
    if election is None or election.phase != "nominations":
        session.close()
        return "phase_closed"
    candidate = session.get(Candidates, candidate_id)
    if candidate is None:
        session.close()
        return "not_found"
    if candidate.status != "nominated":
        session.close()
        return "not_nominated"
    candidate.status = "approved"
    user = session.query(Users).filter(Users.user_name == candidate.roll_no).first()
    if user is not None:
        user.user_type = "candidate"
    session.commit()
    session.close()
    return "approved"

# E5
def withdraw_candidate(candidate_id, roll_no):
    session = Session(engine)
    election = session.query(Election).first()
    if election is None or election.phase != "nominations":
        session.close()
        return "phase_closed"
    candidate = session.get(Candidates, candidate_id)
    if candidate is None:
        session.close()
        return "not_found"
    if candidate.roll_no != roll_no:
        session.close()
        return "roll_mismatch"
    if candidate.status != "approved":
        session.close()
        return "not_approved"
    candidate.status = "withdrawn"
    user = session.query(Users).filter(Users.user_name == candidate.roll_no).first()
    if user is not None:
        user.user_type = "student"
    session.commit()
    session.close()
    return "withdrawn"


# E6
def get_election_phase():
    session = Session(engine)
    election = session.query(Election).first()
    if election is None:
        session.close()
        return "no_election"
    phase = election.phase
    session.close()
    return phase


# E7
def change_phase(phase):
    session = Session(engine)
    election = session.query(Election).first()
    if election is None:
        session.close()
        return "no_election"
        
    if phase != "nominations" and phase != "voting" and phase != "closed":
        session.close()
        return "invalid_phase"

    if phase == "voting":
        for position in POSITIONS:
            candidate = session.query(Candidates).filter(Candidates.position == position,Candidates.status == "approved").first()
            if candidate is None:
                session.close()
                return "no_candidate"
    election.phase = phase
    session.commit()
    session.close()
    return {"phase": phase}


# E8
def cast_vote(voter_roll, candidate_id):
    session = Session(engine)
    election = session.query(Election).first()
    if election is None or election.phase != "voting":
        session.close()
        return "voting_closed"
    candidate = session.get(Candidates, candidate_id)

    if candidate is None:
        session.close()
        return "not_found"

    if candidate.status != "approved":
        session.close()
        return "not_approved"
    position = candidate.position
    existing = session.query(Votes).filter(Votes.voter_roll == voter_roll,Votes.position == candidate.position).first()
    
    if existing is not None:
        session.close()
        return "already_voted"
    vote = Votes(voter_roll=voter_roll,candidate_id=candidate_id,position=position)
    session.add(vote)
    session.commit()
    session.close()
    return {"message": "Vote recorded successfully","voter_roll": voter_roll,"candidate_id": candidate_id,"position": position}


# E9
def get_voted_positions(voter_roll):
    session = Session(engine)
    voted = session.query(Votes).filter(
        Votes.voter_roll == voter_roll).all()
    positions = []
    for vote in voted:
        positions.append(vote.position)
    session.close()
    return {"voted_positions": positions}


# E10
def get_results():
    session = Session(engine)
    election = session.query(Election).first()
    if election is None or election.phase != "closed":
        session.close()
        return "not_closed"
    results = {}

    for position in POSITIONS:
        candidates = session.query(Candidates).filter(
            Candidates.position == position,
            Candidates.status == "approved").all()
        position_results = []

        for candidate in candidates:
            count = session.query(Votes).filter(Votes.candidate_id == candidate.id).count()
            position_results.append({"candidate_id": candidate.id,"name": candidate.name,"votes": count})
        highest_votes = 0

        for item in position_results:
            if item["votes"] > highest_votes:
                highest_votes = item["votes"]
        winner = "No votes"
        winner_count = 0

        for item in position_results:
            if highest_votes > 0 and item["votes"] == highest_votes:
                winner = item
                winner_count = winner_count + 1
        if winner_count > 1:
            winner = "Tie"
        results[position] = {"candidates": position_results,"winner": winner}
    session.close()
    return results


# E11
def add_sample_data():
    session = Session(engine)
    if session.query(Candidates).count() == 0:
        sample_candidates = [
            ("AU01", "Toshima", "class_rep",
             "I will represent students and improve communication.", "approved"),

            ("AU02", "Harshitha", "class_rep",
             "I will work towards better student coordination.", "approved"),

            ("AU03", "Adib", "sports_secretary",
             "I will encourage sports activities and teamwork.", "approved"),

            ("AU04", "Hemanth", "sports_secretary",
             "I will organize sports events for everyone.", "nominated"),

            ("AU05", "Samhitha", "cultural_secretary",
             "I will organize cultural programs and celebrations.", "approved"),

            ("AU06", "Darsh", "cultural_secretary",
             "I will encourage creativity and student participation.", "approved"),

            ("AU07", "Shafi", "tech_secretary",
             "I will promote technology and technical events.", "approved"),

            ("AU08", "Sarang", "tech_secretary",
             "I will bring innovative technical activities.", "withdrawn")
        ]

        for candidate in sample_candidates:
            new_candidate = Candidates(
                roll_no=candidate[0],
                name=candidate[1],
                position=candidate[2],
                manifesto=candidate[3],
                status=candidate[4]
            )
            session.add(new_candidate)
        session.commit()
    session.close()
    return "nominated"