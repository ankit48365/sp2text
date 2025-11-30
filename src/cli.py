import argparse
import yaml
# from easymdm.a_start_point import dispatcher
from code_whisper_s2t import start_point

EXAMPLE = """

Just run 

s2t --run

"""

def main():
    """Main function to handle CLI arguments and execute corresponding actions."""
    print(">>> ✅ Speech 2 Text CLI loaded")
    parser = argparse.ArgumentParser(description='Speech 2 text CLI Tool')
    parser.add_argument('--example', action='store_true', help='Show sample code syntax')
    parser.add_argument('--run', action='store_true', help='Start speech to text utility') # pylint: disable=line-too-long

    args = parser.parse_args()

    if args.example:
        print("Usage Information:\n")
        print(EXAMPLE)

    if args.run:
        start_point()

if __name__ == '__main__':
    main()