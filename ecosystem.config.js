module.exports = {
    apps: [{
        name: "sgu-backend",
        script: "uvicorn",
        args: "main:app --host 0.0.0.0 --port 8000",
        interpreter: "python3",
        env: {
            NODE_ENV: "production",
        }
    }]
}
