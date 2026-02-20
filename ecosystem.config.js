module.exports = {
    apps: [{
        name: "sgu-backend",
        script: "venv/bin/python3",
        args: "-m uvicorn main:app --host 127.0.0.1 --port 8010 --proxy-headers",
        env: {
            NODE_ENV: "production",
        }
    }]
}
