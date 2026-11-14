from fastapi import FastAPI, HTTPException, Header, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import functions

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173","http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"])

functions.initialize_database()

USER_TYPE = ["officer", "student", "candidate"]

def check_role(token, allowed_roles):
    username = functions.verify_token(token=token, token_type="access")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user_type = functions.get_user_type(username)
    if user_type not in allowed_roles:
        raise HTTPException(status_code=403, detail="Permission denied")

class UserRegister(BaseModel):
    user_name: str
    password: str

class UserLogin(BaseModel):
    user_name: str
    password: str

@app.post("/login")
def login(user: UserLogin):
    token = functions.verify_login(username=user.user_name, password=user.password)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return token

@app.post("/refresh")
def refresh(refresh_token=Header(None)):
    username = functions.verify_token(token=refresh_token, token_type="refresh")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    user_type = functions.get_user_type(username)
    if not user_type:
        raise HTTPException(status_code=401, detail="User not found")
    access_token = functions.create_token(username=username, token_type="access", user_type=user_type)
    return {"access_token": access_token}

@app.post("/register_user")
def register_user(user: UserRegister):
    if functions.register_user(user_name=user.user_name, password=user.password, user_type="student"):
        return {"message": "User registered successfully"}
    raise HTTPException(status_code=400, detail="User already exists")

# E1
@app.get("/candidates")
def get_candidates(position=None, approved_only=False, token=Header(None)):
    check_role(token, ["officer", "student", "candidate"])
    if position and position not in functions.POSITIONS:
        raise HTTPException(status_code=422, detail="Invalid position")
    return functions.get_all_candidates(position, approved_only)

# E2
@app.get("/candidates/{candidate_id}")
def candidate(candidate_id: int, token=Header(None)):
    check_role(token, ["officer", "student", "candidate"])
    result = functions.get_candidate(candidate_id)
    if result == "not_found":
        raise HTTPException(status_code=404, detail="Candidate not found")
    return result

# E3
@app.post("/candidates")
def nominate(roll_no: str, name: str, position: str, manifesto: str, token=Header(None)):
    check_role(token, ["student"])
    if position not in functions.POSITIONS:
        raise HTTPException(status_code=422, detail="Invalid position")
    if len(manifesto) < 30:
        raise HTTPException(status_code=422, detail="Manifesto must contain at least 30 characters")
    result = functions.add_candidate(roll_no, name, position, manifesto)
    if result == "duplicate_roll":
        raise HTTPException(status_code=400, detail="This roll number already has an active nomination")
    if result == "invalid_position":
        raise HTTPException(status_code=422, detail="Invalid position")
    return {"message": "Candidate nominated successfully"}

# E4 
@app.patch("/candidates/{candidate_id}/approve")
def approve_candidate(candidate_id: int, token=Header(None)):
    check_role(token, ["officer"])
    response = functions.approve_candidate(candidate_id)
    if response == "phase_closed":
        raise HTTPException(status_code=400, detail="Nominations are closed")
    if response == "not_found":
        raise HTTPException(status_code=404, detail="Candidate not found")
    if response == "not_nominated":
        raise HTTPException(status_code=400, detail="Only nominated candidates can be approved")
    return {"message": "Candidate approved successfully"}

# E5
@app.patch("/candidates/{candidate_id}/withdraw")
def withdraw_candidate(candidate_id: int, roll_no: str, token=Header(None)):
    check_role(token, ["candidate"])
    response = functions.withdraw_candidate(candidate_id, roll_no)
    if response == "phase_closed":
        raise HTTPException(status_code=400, detail="Nominations are closed")
    if response == "not_found":
        raise HTTPException(status_code=404, detail="Candidate not found")
    if response == "roll_mismatch":
        raise HTTPException(status_code=403, detail="Roll number does not match the candidate")
    if response == "already_withdrawn":
        raise HTTPException(status_code=400, detail="Candidate is already withdrawn")
    return {"message": "Nomination withdrawn successfully"}

# E6 
@app.get("/election/phase")
def get_election_phase(token=Header(None)):
    check_role(token, ["officer", "student", "candidate"])
    response = functions.get_election_phase()
    if response == "no_election":
        raise HTTPException(status_code=404, detail="Election not found")
    return {"phase": response}

# E7 
@app.patch("/election/phase")
def change_phase(phase: str, token=Header(None)):
    check_role(token, ["officer"])
    result = functions.change_phase(phase)
    if result == "no_election":
        raise HTTPException(status_code=404, detail="Election not found")
    if result == "invalid_phase":
        raise HTTPException(status_code=400, detail="Invalid election phase")
    if result == "no_candidate":
        raise HTTPException(status_code=400, detail="Every position must have at least one approved candidate")
    return result

# E8 
@app.post("/votes")
def vote(voter_roll: str, candidate_id: int, token=Header(None)):
    check_role(token, ["student"])
    if voter_roll == "":
        raise HTTPException(status_code=422, detail="Empty roll number")
    result = functions.cast_vote(voter_roll, candidate_id)
    if result == "voting_closed":
        raise HTTPException(status_code=400, detail="Voting is not open")
    if result == "not_found":
        raise HTTPException(status_code=404, detail="Candidate not found")
    if result == "not_approved":
        raise HTTPException(status_code=400, detail="Candidate not approved")
    if result == "already_voted":
        raise HTTPException(status_code=400, detail="Already voted for this position")
    return result

# E9 
@app.get("/votes/{voter_roll}/positions")
def voted_positions(voter_roll: str, token=Header(None)):
    check_role(token, ["student"])
    return functions.get_voted_positions(voter_roll)

# E10
@app.get("/results")
def get_final_results(token=Header(None)):
    check_role(token, ["officer", "student", "candidate"])
    result = functions.get_results()
    if result == "not_closed":
        raise HTTPException(status_code=403, detail="Election is not closed")
    return result