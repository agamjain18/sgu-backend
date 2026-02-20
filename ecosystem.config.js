module.exports = {
    apps: [{
        name: "sgu-backend",
        script: "venv/bin/python3",
        args: "-m uvicorn main:app --host 0.0.0.0 --port 8010 --proxy-headers",
        env: {
            NODE_ENV: "production",
        }
    }]
}
