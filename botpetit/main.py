from dotenv import load_dotenv
load_dotenv()
import os
import discord
from discord.ext import commands

# NUNCA coloque o token direto no código.
# Defina a variável de ambiente DISCORD_TOKEN antes de rodar:
#   Windows (PowerShell): $env:DISCORD_TOKEN="seu_token_aqui"
#   Linux/Mac:             export DISCORD_TOKEN="seu_token_aqui"
TOKEN = os.getenv("DISCORD_TOKEN")

GIF_HELP = "https://klipy.com/gifs/meowl-goodnight"

if not TOKEN:
    raise RuntimeError(
        "Token não encontrado. Defina a variável de ambiente DISCORD_TOKEN "
        "antes de rodar o bot."
    )

# Se quiser sync instantâneo dos comandos durante testes, coloque aqui o ID
# do seu servidor (clique direito no servidor -> Copiar ID, com o modo
# desenvolvedor ativado no Discord). Deixe None para sync global (demora
# até 1h para propagar).
GUILD_ID = None  # ex: 123456789012345678

intents = discord.Intents.default()
intents.members = True  # lembre-se de habilitar "Server Members Intent" no Developer Portal

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


# ==========================
# MENU DOS ELEMENTOS
# ==========================

class ElementoSelect(discord.ui.Select):

    def __init__(self, familia):

        elementos = {
            "gases": [
                ("Hélio (He)", "Hélio (He)"),
                ("Neônio (Ne)", "Neônio (Ne)"),
                ("Argônio (Ar)", "Argônio (Ar)"),
                ("Criptônio (Kr)", "Criptônio (Kr)"),
                ("Xenônio (Xe)", "Xenônio (Xe)"),
                ("Radônio (Rn)", "Radônio (Rn)")
            ],
            "alcalinos": [
                ("Lítio (Li)", "Lítio (Li)"),
                ("Sódio (Na)", "Sódio (Na)"),
                ("Potássio (K)", "Potássio (K)")
            ],
            "transicao": [
                ("Ferro (Fe)", "Ferro (Fe)"),
                ("Cobre (Cu)", "Cobre (Cu)"),
                ("Ouro (Au)", "Ouro (Au)")
            ],
            "nao_metais": [
                ("Carbono (C)", "Carbono (C)"),
                ("Oxigênio (O)", "Oxigênio (O)"),
                ("Nitrogênio (N)", "Nitrogênio (N)")
            ]
        }

        options = [
            discord.SelectOption(label=nome, value=valor)
            for nome, valor in elementos[familia]
        ]

        super().__init__(
            placeholder="Escolha seu elemento...",
            options=options
        )

    async def callback(self, interaction: discord.Interaction):

        elemento = self.values[0]

        cargo = discord.utils.get(
            interaction.guild.roles,
            name=elemento
        )

        if cargo is None:
            await interaction.response.send_message(
                f"❌ Não encontrei o cargo **{elemento}** no servidor. "
                "Crie um cargo com esse nome exato (incluindo o símbolo entre parênteses).",
                ephemeral=True
            )
            return

        try:
            await interaction.user.add_roles(cargo)
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ Não tenho permissão para atribuir esse cargo. "
                "Verifique se o cargo do bot está **acima** do cargo do elemento "
                "na lista de cargos do servidor (Configurações > Cargos).",
                ephemeral=True
            )
            return
        except discord.HTTPException:
            await interaction.response.send_message(
                "❌ Ocorreu um erro ao atribuir o cargo. Tente novamente.",
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            f"✅ Você agora é **{elemento}**!",
            ephemeral=True
        )


class ElementoView(discord.ui.View):

    def __init__(self, familia):
        super().__init__()
        self.add_item(ElementoSelect(familia))


# ==========================
# MENU DAS FAMÍLIAS
# ==========================

class FamiliaSelect(discord.ui.Select):

    def __init__(self):

        options = [
            discord.SelectOption(label="Metais alcalinos", emoji="🔋", value="alcalinos"),
            discord.SelectOption(label="Metais de transição", emoji="⚙️", value="transicao"),
            discord.SelectOption(label="Não metais", emoji="🌱", value="nao_metais"),
            discord.SelectOption(label="Gases nobres", emoji="🎈", value="gases"),
        ]

        super().__init__(
            placeholder="Escolha uma família...",
            options=options
        )

    async def callback(self, interaction: discord.Interaction):

        familia = self.values[0]

        await interaction.response.send_message(
            "⚛️ Agora escolha seu elemento:",
            view=ElementoView(familia),
            ephemeral=True
        )


class FamiliaView(discord.ui.View):

    def __init__(self):
        super().__init__()
        self.add_item(FamiliaSelect())


# ==========================
# BOT ONLINE
# ==========================

@bot.event
async def on_ready():

    if GUILD_ID:
        guild = discord.Object(id=GUILD_ID)
        bot.tree.copy_global_to(guild=guild)
        await bot.tree.sync(guild=guild)
    else:
        await bot.tree.sync()

    print(f"Bot conectado como {bot.user}")


# ==========================
# COMANDO /ELEMENTO
# ==========================

@bot.tree.command(
    name="element",
    description="choose your role"
)
async def elemento(interaction: discord.Interaction):

    await interaction.response.send_message(
        "🧪 Escolha a família do seu elemento:",
        view=FamiliaView(),
        ephemeral=True
    )

# ==========================
# COMANDO /HELP (PIADA)
# ==========================

@bot.tree.command(
    name="help",
    description="???"
)
async def help(interaction: discord.Interaction):

    await interaction.response.send_message(
        GIF_HELP
    )

bot.run(TOKEN)