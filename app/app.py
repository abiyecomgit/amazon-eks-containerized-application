from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return """
    <h1>Containerized Application on Amazon EKS</h1>
    <p>Application successfully deployed to Amazon EKS using Helm!</p>
    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
