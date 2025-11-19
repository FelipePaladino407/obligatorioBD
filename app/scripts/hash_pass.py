import argparse
import bcrypt

def main() -> None:
    parser = argparse.ArgumentParser(description="Generar hash bcrypt para una contraseña")
    parser.add_argument("password", help="Contraseña a hashear")
    args = parser.parse_args()

    hashed = bcrypt.hashpw(args.password.encode("utf-8"), bcrypt.gensalt())
    print("Hash:", hashed.decode("utf-8"))


if __name__ == "__main__":
    main()
