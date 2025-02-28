import argparse
import PyInstaller.__main__

def main():
    parser = argparse.ArgumentParser(description='Paneer CLI.')
    parser.add_argument('--build', action='store_true', help='Build the application')

    args = parser.parse_args()

    if args.build:
        PyInstaller.__main__.run(["main.py", '--add-data', "gui/:gui"])
    else:
        print(f'u need help?')
        parser.print_help()

if __name__ == '__main__':
    main()
