import argparse
import json
import logging
import signal
import sys
import time
from datetime import datetime
from pathlib import Path

from colorama import Fore, Style, init as colorama_init

from deepai import Ai, AiError

logger = logging.getLogger(__name__)

DEFAULT_TOPICS = [
    "What is the meaning of life?",
    "Do robots dream of electric sheep?",
    "Is water wet?",
    "What came first, the chicken or the egg?",
]

DEFAULT_ROUNDS = 500
DEFAULT_DELAY = 1.0

shutdown_requested = False


def handle_signal(signum, frame):
    global shutdown_requested
    shutdown_requested = True
    print(f"\n{Fore.YELLOW}Shutdown requested. Finishing current round...{Style.RESET_ALL}")


def setup_logging(log_file):
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout),
        ],
    )


def parse_args():
    parser = argparse.ArgumentParser(
        description="DumbAi - Two AI chatbots talking to each other"
    )
    parser.add_argument(
        "-n", "--rounds",
        type=int,
        default=DEFAULT_ROUNDS,
        help=f"Number of conversation rounds (default: {DEFAULT_ROUNDS})"
    )
    parser.add_argument(
        "-t", "--topic",
        type=str,
        default=None,
        help="Initial topic/question for the conversation"
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default="conversation.json",
        help="Output file path for conversation history (default: conversation.json)"
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=DEFAULT_DELAY,
        help=f"Delay in seconds between messages (default: {DEFAULT_DELAY})"
    )
    parser.add_argument(
        "--log-file",
        type=str,
        default="dumbai.log",
        help="Log file path (default: dumbai.log)"
    )
    parser.add_argument(
        "--api-key",
        type=str,
        default=None,
        help="DeepAI API key (default: built-in trial key)"
    )
    parser.add_argument(
        "--api-url",
        type=str,
        default=None,
        help="DeepAI API URL"
    )
    parser.add_argument(
        "--name1",
        type=str,
        default="eldorado1",
        help="Name of first bot (default: eldorado1)"
    )
    parser.add_argument(
        "--name2",
        type=str,
        default="eldorado2",
        help="Name of second bot (default: eldorado2)"
    )
    return parser.parse_args()


def save_conversation(history, filepath):
    try:
        with open(filepath, "w") as f:
            json.dump(history, f, indent=2)
        logger.info(f"Conversation saved to {filepath}")
    except IOError as e:
        logger.error(f"Failed to save conversation: {e}")


def print_message(bot_name, color, round_num, text):
    print(f"{color}{bot_name} [{round_num}] : {Style.RESET_ALL}{text}")


def main():
    args = parse_args()
    colorama_init()
    setup_logging(args.log_file)

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    logger.info("DumbAi starting up")
    logger.info(f"Rounds: {args.rounds}, Delay: {args.delay}s, Output: {args.output}")

    bot1 = Ai(name=args.name1, api_key=args.api_key, api_url=args.api_url)
    bot2 = Ai(name=args.name2, api_key=args.api_key, api_url=args.api_url)

    topic = args.topic or DEFAULT_TOPICS[0]
    logger.info(f"Initial topic: {topic}")

    print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}  DumbAi - {bot1.name} vs {bot2.name}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}  Topic: {topic}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}\n")

    conversation_history = []
    bot2_answer = f"Hi im {bot2.name}, how can I assist you?"

    for round_num in range(1, args.rounds + 1):
        if shutdown_requested:
            logger.info("Shutdown requested, stopping gracefully")
            break

        try:
            bot1_answer = bot1.ask(bot2_answer)
            print_message(bot1.name, Fore.GREEN, round_num, bot1_answer)
            conversation_history.append({
                "round": round_num,
                "model": bot1.name,
                "text": bot1_answer,
                "timestamp": datetime.now().isoformat(),
            })
            logger.debug(f"[{bot1.name}] Round {round_num}: {bot1_answer}")

            if shutdown_requested:
                break

            if args.delay > 0:
                time.sleep(args.delay)

            bot2_answer = bot2.ask(bot1_answer)
            print_message(bot2.name, Fore.RED, round_num, bot2_answer)
            conversation_history.append({
                "round": round_num,
                "model": bot2.name,
                "text": bot2_answer,
                "timestamp": datetime.now().isoformat(),
            })
            logger.debug(f"[{bot2.name}] Round {round_num}: {bot2_answer}")

            if args.delay > 0:
                time.sleep(args.delay)

            if round_num % 10 == 0:
                save_conversation(conversation_history, args.output)
                logger.info(f"Progress: {round_num}/{args.rounds} rounds completed")

        except AiError as e:
            logger.error(f"AI error at round {round_num}: {e}")
            print(f"{Fore.RED}Error at round {round_num}: {e}. Retrying in 5s...{Style.RESET_ALL}")
            time.sleep(5)
            continue

    save_conversation(conversation_history, args.output)
    print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}  Conversation finished. {len(conversation_history)} messages saved to {args.output}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")


if __name__ == "__main__":
    main()
