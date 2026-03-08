import discord, asyncio, shutil, re, os, json
from colorama import Fore, init

with open("config.json", "r") as file:
    data = json.load(file)

init(autoreset = True)

online_users = set()

def visible_length(s):
    return len(re.sub(r'\x1b\[[0-9;]*m', '', s))

def build_box():
    lines = []
    lines.append(Fore.CYAN + "┌" + "─" * 40 + "┐")

    padding_left = (40 - len("Discord Token Onliner")) // 2
    padding_right = 40 - len("Discord Token Onliner") - padding_left

    lines.append(Fore.CYAN + "│" + " " * padding_left + Fore.WHITE + "Discord Token Onliner" + Fore.CYAN + " " * padding_right + "│")
    lines.append(Fore.CYAN + "├" + "─" * 40 + "┤")

    if online_users:
        for user in sorted(online_users):
            max_user_len = 40 - visible_length(f"{Fore.WHITE}| " + f"   {Fore.GREEN}ONLINE    ")

            display_user = user
            if len(display_user) > max_user_len:
                display_user = display_user[:max_user_len - 3] + "..."

            space_for_username = max_user_len
            pad_left = (space_for_username - len(display_user)) // 2
            pad_right = space_for_username - len(display_user) - pad_left

            line_content = " " * pad_left + Fore.BLUE + display_user + " " * pad_right + f"{Fore.WHITE}| " + f"   {Fore.GREEN}ONLINE    "
            lines.append(Fore.CYAN + "│" + line_content + "│")
    else:
        lines.append(Fore.CYAN + "│" + " " * 40 + "│")

    lines.append(Fore.CYAN + "├" + "─" * 40 + "┤")

    pad_left = (40 - len(f"{Fore.WHITE}made by @s.eths | v{data['version']}")) // 2
    pad_right = 40 - len(f"{Fore.WHITE}made by @s.eths | v{data['version']}") - pad_left

    lines.append(Fore.CYAN + "│   " + " " * pad_left + f"{Fore.WHITE}made by @s.eths | v{data['version']}" + " " * pad_right + Fore.CYAN + "  │")
    lines.append(Fore.CYAN + "└" + "─" * 40 + "┘")

    return lines

def box_centered():
    size = shutil.get_terminal_size()
    term_width, term_height = size.columns, size.lines

    lines = build_box()

    vertical_padding = (term_height - len(lines)) // 2
    print("\n" * vertical_padding, end = "")

    for line in lines:
        padding = (term_width - visible_length(line)) // 2
        print(" " * padding + line)

async def start_client(token, delay):
    await asyncio.sleep(delay)
    client = discord.Client()

    @client.event
    async def on_ready():
        online_users.add(client.user.name)
        print("\033[H\033[J", end = "")
        box_centered()

    await client.start(token)

async def main():
    os.system("cls")
    print("\033[?25l", end = "")
    box_centered()

    tasks = [
        asyncio.create_task(start_client(token, i * 5))
        for i, token in enumerate(data["tokens"])
    ]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())