def test_health(client):
    r=client.get("/health")
    assert r.status_code==200 and r.json()["status"]=="ok"

def test_home(client):
    r=client.get("/")
    assert r.status_code==200 and "Build your plan" in r.text

def test_generate_and_feedback(client):
    r=client.post("/generate-workout",data={"username":"Test User","user_id":"test01","age":"28","weight":"72.5","goal":"general_wellness","intensity":"medium"})
    assert r.status_code==200 and "personalized plan is ready" in r.text and "Day 1" in r.text
    r=client.post("/submit-feedback",data={"user_id":"test01","feedback":"Add yoga and make the plan easier."})
    assert r.status_code==200 and "plan has been updated" in r.text and "Yoga-inspired mobility" in r.text

def test_users_page(client):
    client.post("/generate-workout",data={"username":"Test User","user_id":"test01","age":"28","weight":"72.5","goal":"general_wellness","intensity":"medium"})
    r=client.get("/view-all-users")
    assert r.status_code==200 and "Test User" in r.text
