from app import create_app

app = create_app()

if __name__ == "__main__":
    print("=== URL MAP ===")
    print(app.url_map)
    print("===============")
    app.run(host="127.0.0.1", port=8080, debug=True)
