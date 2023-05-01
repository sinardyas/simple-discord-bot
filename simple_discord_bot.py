import discord
import requests
import os

API_ENDPOINT = os.environ.get('API_ENDPOINT')

class Dropdown(discord.ui.Select):
    def __init__(self, _bot: discord.Bot, _address):
        # For example, you can use self.bot to retrieve a user or perform other functions in the callback.
        # Alternatively you can use Interaction.client, so you don't need to pass the bot instance.
        self.bot = _bot
        self.address = _address
        self.service_api = ServiceApi()

        # Set the options that will be presented inside the dropdown:
        options = [
            discord.SelectOption(label="Point", emoji="🟥"),
            discord.SelectOption(label="Diamond", emoji="🟩"),
        ]

        # The placeholder is what will be shown when no option is selected.
        # The min and max values indicate we can only pick one of the three options.
        # The options parameter, contents shown above, define the dropdown options.
        super().__init__(
            placeholder="Choose your token to mint...",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        # Use the interaction object to send a response message containing
        # the user's favourite colour or choice. The self object refers to the
        # Select object, and the values attribute gets a list of the user's
        # selected options. We only want the first one.

        await interaction.response.send_message("Minting token....")

        is_success = False
        if self.values[0] == "Point":
            is_success = await self.service_api.mint_token("POINT", self.address, 1)
        else:
            is_success = await self.service_api.mint_token("DIAMOND", self.address, 1)

class DropdownView(discord.ui.View):
    def __init__(self, _bot: discord.Bot, address):
        self.bot = _bot

        # Initializing the view and adding the dropdown can actually be done in a one-liner if preferred:
        super().__init__(Dropdown(self.bot, address))

class ServiceApi():
    def __init__(self):
        self.basic_auth = f"Basic {os.environ.get('BASIC_AUTH')}"

    async def mint_token(self, token, address, amount) -> bool:
        # Make an API request to retrieve the wallet information
        # Set the request parameters
        url = f"{API_ENDPOINT}/v1/wallet/mint"
        headers = {
            "Authorization": self.basic_auth,
            "Content-Type": "application/x-www-form-urlencoded",
        }
        payload = {
            "tokenName": token,
            "amount": amount,
            "recipientAddress": address,
        }

        # Send the API request
        response = requests.post(url, headers=headers, data=payload)

        # Check if the API request was successful
        if response.status_code == 200:
            wallet_data = response.json()
            # Replace with your desired response message
            response_msg = "Success!"
            return True
        else:
            # Replace with your error response message
            response_msg = "Error retrieving wallet information."
            return False

    async def check_balance(self, address):
        # Make an API request to retrieve the wallet information
        # Set the request parameters
        url = f"{API_ENDPOINT}/v1/wallet/check-user-balance?walletAddress={address}"
        headers = {
            "Authorization": self.basic_auth,
            "Content-Type": "application/x-www-form-urlencoded",
        }
        # Send the API request
        response = requests.get(url, headers=headers)

        # Check if the API request was successful
        if response.status_code == 200:
            json_response = response.json()
            wallet_data = json_response['data']
            print(wallet_data)

            response_msg = "Success!"
            return wallet_data['balance']
        else:
            response_msg = "Error retrieving wallet information."
            return None

class SimpleDiscordBot():
    def __init__(self):
        self.bot = discord.Bot()
        self.__init_bot()

    def __init_bot(self): 
        @self.bot.slash_command()
        async def mint(ctx: discord.ApplicationContext, address):
            """Sends a message with our dropdown that contains token options."""

            view = DropdownView(self.bot, address)

            await ctx.respond("Pick your token to be mint:", view=view)

        @self.bot.slash_command()
        async def balance(ctx: discord.ApplicationContext, address):
            """Check user balance by username"""

            service_api = ServiceApi()
            balance = await service_api.check_balance(address)

            if balance is None:
                await ctx.respond("Error")
            else:
                await ctx.respond(f"Diamond: {balance['diamond']:,d}; Point: {balance['point']:,d}")

        @self.bot.event
        async def on_ready():
            print(f"Logged in as {self.bot.user} (ID: {self.bot.user.id})")
            print("------")   

    def run(self):
        self.bot.run(os.environ.get('DISCORD_BOT_TOKEN'))

simple_discord_bot = SimpleDiscordBot()
simple_discord_bot.run()