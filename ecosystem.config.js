module.exports = {
    apps: [{
        name: "sgu-backend",
        script: "./venv/bin/python3",
        args: "-m uvicorn main:app --host 0.0.0.0 --port 8022 --proxy-headers --root-path /sgu",
        interpreter: "none",
        env: {
            NODE_ENV: "production",
        }
    }]
}
