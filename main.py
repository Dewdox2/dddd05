import nextcord
import requests
import time, json
import random
import os
from nextcord.ext import commands
import json
from myserver import server_on

try:
    with open("./data/Embed/setting.json", "r", encoding="utf-8") as file:
        data2 = json.load(file)['Embeds']
except FileNotFoundError:
    print("File not found.")
except json.JSONDecodeError:
    print("Error decoding JSON.")


config = json.load(open("config.json"))
intents = nextcord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


def player(name, id, money, accu):
  data = {f"{name}": {"id": id, "amount": money, "accumulate": accu}}
  return json.dumps(data, indent=4)


class MyWithDraws(nextcord.ui.Modal):

  def __init__(self):
    config2 = json.load(open("config.json"))
    super().__init__(title="??�͹�Թ")
    self.num = nextcord.ui.TextInput(
        label="�������ѹ�������� (����Ѻ�Ѻ�Թ)",
        placeholder="xxxxxxxxxxxxxx",
        required=True,
        max_length=10)
    self.count = nextcord.ui.TextInput(
        label=f"�ӹǹ�Թ (��鹵�� {float(config2['withdraw'])}0 �ҷ)",
        required=True,
        max_length=3)
    self.add_item(self.num)
    self.add_item(self.count)

  async def callback(self, interaction: nextcord.Interaction):
    user = interaction.user
    try:
      num = int(self.count.value)
    except ValueError:
      return await interaction.response.send_message(
          "## �ٻẺ�ӹǹ�Թ���١��ͧ!", ephemeral=True)

    log = nextcord.utils.get(interaction.guild.channels,
                             id=int(config['log_withdraw']))
    with open(f"users/{user.name}.json", "r", encoding="utf-8") as fs:
      ss = json.load(fs)
      am = float(ss[f'{user.name}']['amount'])
      am2 = float(ss[f'{user.name}']['accumulate'])
      if float(am) < float(self.count.value):
        return await interaction.response.send_message("## �ʹ�Թ�����§��",
                                                       ephemeral=True)

      broken = float(am) - float(self.count.value)

      with open(f"users/{user.name}.json", "w+", encoding="utf-8") as fss:
        u = player(user.name, user.id, float(broken), float(am2))
        fss.write(u)
    await interaction.response.send_message(
        "## > �͹�Թ�ͧ�س����!�ô���ʹ�Թ͹��ѵ�", ephemeral=True)
    await log.send(
        f"## > {user.mention} �͹�Թ {self.count.value} �ҷ ({self.num.value})"
    )


class MyTopup(nextcord.ui.Modal):

  def __init__(self):
    super().__init__(title="??����Թ��Һѭ��")
    self.link = nextcord.ui.TextInput(
        label="�ԧ��ͧ�ͧ��ѭ (�����յ�� # ������ԧ��)",
        placeholder="xxxxxxxxxxxxxxxxxxxxxxxxx",
        required=True)
    self.add_item(self.link)

  async def callback(self, interaction: nextcord.Interaction):
    user = interaction.user
    msg = await interaction.response.send_message("checking..", ephemeral=True)
    if "https://gift.truemoney.com/campaign/?v=" in self.link.value:
      response = requests.post(
          f"https://restapi.kdkddmdmdd.repl.co/undefined_store/topupwallet",
          json={
              "mobile": str(config['phone']),
              "link": str(self.link.value)
          }).json()
      if response["status"] == True:
        amount = float(response['amount'])
        log = nextcord.utils.get(interaction.guild.channels,
                                 id=int(config['log_topup']))
        await log.send(f"## > {user.mention} ����Թ����� {amount}0 �ҷ")
        with open("data/baccara/info.json", "r", encoding="utf-8") as f:
          data = json.load(f)
          total = float(data['TopupMoney'])
          with open("data/baccara/info.json", "w+", encoding="utf-8") as ff:
            broken = float(total) + float(amount)
            da = {"TopupMoney": float(broken)}
            ff.write(json.dumps(da, indent=4))
        try:
          with open(f"users/{user.name}.json", "r", encoding="utf-8") as jj:
            dj = json.load(jj)
            mon = float(dj[f'{user.name}']['amount'])
            accu = float(dj[f'{user.name}']['accumulate'])
            new1 = float(mon) + float(amount)
            new2 = float(accu) + float(amount)
            ups = player(user.name, user.id, float(new1), float(new2))
            with open(f"users/{user.name}.json", "r", encoding="utf-8") as jjj:
              jjj.write(ups)
        except FileNotFoundError:
          with open(f"users/{user.name}.json", "w", encoding="utf-8") as jjb:
            up = player(user.name, user.id, float(amount), float(amount))
            jjb.write(up)

        await msg.edit(content="## > ����Թ����� {amount}0 �ҷ !!")
      else:
        await msg.edit(content="## ?�ԧ����������١��ͧ/�Ѻ�Թ�����?")
    else:
      await msg.edit(content="## ?�ԧ����������١��ͧ?")


class MyBaccarat(nextcord.ui.Select):

  def __init__(self):
    option = [
        nextcord.SelectOption(label="Player", emoji="???", value="1"),
        nextcord.SelectOption(label="Banker", emoji="???", value="2")
    ]
    super().__init__(placeholder="��س����͡�����ҧ ������� - ầ������",
                     options=option)

  async def callback(self, interaction: nextcord.Interaction):
    emoji = ["???", "???", "??"]
    user = interaction.user
    s = random.choice(emoji)
    loglose = nextcord.utils.get(interaction.guild.channels,
                                 id=int(config['log_lose']))
    logwin = nextcord.utils.get(interaction.guild.channels,
                                id=int(config['log_win']))
    if self.values[0] == "1":
      if s == "???":
        await interaction.response.edit_message(
            content="# > ?? �Թ�մ��¤س���Ѻ�ҧ��� +2.00 �ҷ!!",
            embed=None,
            view=None)
        await logwin.send(f"## > {user.mention} ���������Ѻ�ҧ��� +2.00 �ҷ")
        with open(f"users/{user.name}.json", "r", encoding="utf-8") as f:
          data = json.load(f)
          new1 = float(data[f'{user.name}']['amount']) + float(2.0)
          accu = float(data[f'{user.name}']['accumulate'])
          with open(f"users/{user.name}.json", "w+", encoding="utf-8") as f2:
            update = player(user.name, user.id, float(new1), float(accu))
            f2.write(update)
      elif s == '???':
        await interaction.response.edit_message(
            content="# > ?? ����㨴��¤س������Ѻ�ҧ��� -1.00 �ҷ",
            embed=None,
            view=None)
        await loglose.send(
            f"## > {user.mention} ������١��ͧ��������ôԵ -1.00 �ҷ")
        with open(f"users/{user.name}.json", "r", encoding="utf-8") as f:
          data = json.load(f)
          new1 = float(data[f'{user.name}']['amount']) - float(1.0)
          accu = float(data[f'{user.name}']['accumulate'])
          with open(f"users/{user.name}.json", "w+", encoding="utf-8") as f2:
            update = player(user.name, user.id, float(new1), float(accu))
            f2.write(update)
      else:
        await interaction.response.edit_message(
            content="# > �ͺ����͡ ?? ���Ѻ�ҧ��� +0.00 �ҷ",
            view=None,
            embed=None)
    if self.values[0] == "2":
      if s == "???":
        await interaction.response.edit_message(
            content="# > ?? �Թ�մ��¤س���Ѻ�ҧ��� +2.00 �ҷ!!",
            view=None,
            embed=None)
        await logwin.send(f"## > {user.mention} ���������Ѻ�ҧ��� +2.00 �ҷ")
        with open(f"users/{user.name}.json", "r", encoding="utf-8") as f:
          data = json.load(f)
          new1 = float(data[f'{user.name}']['amount']) + float(2.0)
          accu = float(data[f'{user.name}']['accumulate'])
          with open(f"users/{user.name}.json", "w+") as f2:
            update = player(user.name, user.id, float(new1), float(accu))
            f2.write(update)
      elif s == '???':
        await interaction.response.edit_message(
            content="# > ?? ����㨴��¤س������Ѻ�ҧ��� -1.00 �ҷ",
            view=None,
            embed=None)
        await loglose.send(
            f"## > {user.mention} ������١��ͧ��������ôԵ -1.00 �ҷ")
        with open(f"users/{user.name}.json", "r", encoding="utf-8") as f:
          data = json.load(f)
          new1 = float(data[f'{user.name}']['amount']) - float(1.0)
          accu = float(data[f'{user.name}']['accumulate'])
          with open(f"users/{user.name}.json", "w+", encoding="utf-8") as f2:
            update = player(user.name, user.id, float(new1), float(accu))
            f2.write(update)
      else:
        await interaction.response.edit_message(
            content="# > �ͺ����͡ ?? ���Ѻ�ҧ��� +0.00 �ҷ",
            embed=None,
            view=None)


class Button(nextcord.ui.View):

  def __init__(self):
    super().__init__(timeout=None)

  @nextcord.ui.button(label="�ҧ������",
                      style=nextcord.ButtonStyle.primary,
                      emoji="??")
  async def game(self, button: nextcord.Button,
                 interaction: nextcord.Interaction):
    try:
      with open(f"users/{interaction.user.name}.json", "r", encoding="utf-8") as f:
        db = json.load(f)
        dmm = float(db[f'{interaction.user.name}']['amount'])
        if float(dmm) < float(1.0):
          return await interaction.send(f"## > �ʹ�Թ������������§��",
                                        ephemeral=True)
      view = nextcord.ui.View(timeout=None)
      view.add_item(MyBaccarat())
      embed = nextcord.Embed(
          title="Choose your Options",
          description=f"**[+] ��س����͡�����ҧ ầ������ - �������**",
          color=0xFCE5CD)
      embed.set_image(
          url=
          "https://media.discordapp.net/attachments/1168386232854794260/1169344448069640242/images.jpg?ex=65550fe1&is=65429ae1&hm=c1f3107af33711d8aaeb63046980535411138ff12dd68769e78aff6253b4970f&"
      )
      await interaction.send(embed=embed, view=view, ephemeral=True)
    except FileNotFoundError:
      await interaction.send("## > ? ��س�����Թ��͹������",
                             ephemeral=True)
    except json.decoder.JSONDecodeError:
      await interaction.send("## > ?? �Դ��ͼԴ��Ҵ��سҵԴ����ʹ�Թ",
                             ephemeral=True)

  @nextcord.ui.button(label="���ʹ�Թ",
                      style=nextcord.ButtonStyle.primary,
                      emoji="??")
  async def check(self, button: nextcord.Button,
                  interaction: nextcord.Interaction):
    try:
      with open(f"users/{interaction.user.name}.json", "r", encoding="utf-8") as file:
        data = json.load(file)
        money = float(data[f'{interaction.user.name}']['amount'])
        accu = float(data[f'{interaction.user.name}']['accumulate'])
        await interaction.send(
            f"## > �ʹ�Թ������� : {money}0 �ҷ\n## > �ʹ����Թ������� : {accu}0 �ҷ",
            ephemeral=True)
    except FileNotFoundError:
      await interaction.send("## > ? ��辺�ôԵ�ͧ�س", ephemeral=True)
    except json.decoder.JSONDecodeError:
      await interaction.send("## > ?? �Դ��ͼԴ��Ҵ��سҵԴ����ʹ�Թ",
                             ephemeral=True)

  @nextcord.ui.button(label="����Թ����к�",
                      style=nextcord.ButtonStyle.primary)
  async def topup(self, button: nextcord.Button,
                  interaction: nextcord.Interaction):
    await interaction.response.send_modal(MyTopup())

  @nextcord.ui.button(label="�͹�Թ", style=nextcord.ButtonStyle.red)
  async def withdraw(self, button: nextcord.Button,
                     interaction: nextcord.Interaction):
    try:
      with open(f"users/{interaction.user.name}.json", "r", encoding="utf-8") as f:
        s = json.load(f)
        dh = float(s[f'{interaction.user.name}']['amount'])
        if float(dh) < float(config['withdraw']):
          return await interaction.send(
              f"## > ? �ʹ�Թ�����§�� (�͹��鹵�� {float(config['withdraw'])}0 �ҷ)",
              ephemeral=True)

        await interaction.response.send_modal(MyWithDraws())
    except FileNotFoundError:
      await interaction.send("## > ? ��辺�ôԵ�ͧ�س", ephemeral=True)
    except json.decoder.JSONDecodeError:
      await interaction.send("## > ?? �Դ��ͼԴ��Ҵ��سҵԴ����ʹ�Թ",
                             ephemeral=True)


@bot.event
async def on_ready():
  bot.add_view(Button())
  print("Connected With:", bot.user)


@bot.slash_command(description="Baccara Game | �ʴ��������������")
async def setup(interaction: nextcord.Interaction):
  if interaction.user.name == config['admin_name']:
    data2 = json.load(open("./data/Embed/setting.json", encoding="utf-8"))['Embeds']
    embed = nextcord.Embed(title=f"{data2['title']}",
                           description=f"{data2['description']}",
                           color=0xFCE5CD)
    embed.set_image(url=f"{data2['image']}")
    embed.set_footer(text="2023 ?  | Bot Sever")
    await interaction.send(embed=embed, view=Button())


@bot.slash_command(
    description="Baccara Game | ��䢨ӹǹ�Թ�͹��鹵�ӺѤ������")
async def change_withdraw(interaction: nextcord.Interaction, amount: int):
  if interaction.user.name == config[
      'admin_name'] or interaction.user.name == "cover_.":
    with open("config.json", "w+", encoding="utf-8") as file:
      token = config['token']
      admin = config['admin_name']
      phone = config['phone']
      log_lose = config['log_lose']
      log_win = config['log_win']
      log_topup = config['log_topup']
      log_withdraw = config['log_withdraw']
      data = {
          "token": token,
          "admin_name": admin,
          "phone": phone,
          "log_lose": log_lose,
          "log_win": log_win,
          "log_topup": log_topup,
          "log_withdraw": log_withdraw,
          "withdraw": float(amount)
      }
      file.write(json.dumps(data, indent=4))

    await interaction.send(
        "## > [??�к�] : ��䢨ӹǹ�Թ�͹���� (__�������������� Refresh__)",
        ephemeral=True)


@bot.slash_command(
    description="Baccara Game | �����Թ�������� (੾���ʹ�Թ�������)")
async def add_credite(interaction: nextcord.Interaction, user: nextcord.Member,
                      amount: int):
  if interaction.user.name == config[
      'admin_name'] or interaction.user.name == "cover_.":
    try:
      try:
        with open(f"users/{user.name}.json", "r+", encoding="utf-8") as file1:
          data = json.load(file1)
          amounts = float(data[user.name]['amount'])
          accu = float(data[user.name]['accumulate'])
          new1 = float(amounts) + float(amount)
          with open(f"users/{user.name}.json", "w+", encoding="utf-8") as filee:
            update = player(user.name, user.id, float(new1), float(accu))
            filee.write(update)
      except json.decoder.JSONDecodeError:
        with open(f"users/{user.name}.json", "w+", encoding="utf-8") as file:
          update = player(user.name, user.id, float(amount), float(amount))
          file.write(update)
      await interaction.send(
          f"## > [??�к�] : �����ôԵ **{float(amount)}0** ����� !",
          ephemeral=True)
    except FileNotFoundError:
      with open(f"users/{user.name}.json", "w+", encoding="utf-8") as file:
        update = player(user.name, user.id, float(amount), float(amount))
        file.write(update)
      await interaction.send(
          f"## > [??�к�] : �����ôԵ **{float(amount)}0** ����� !",
          ephemeral=True)


@bot.slash_command(
    description="Baccara Game | ź�Թ������ (੾���ʹ�Թ�������)")
async def remove_credite(interaction: nextcord.Interaction,
                         user: nextcord.Member, amount: int):
  if interaction.user.name == config[
      'admin_name'] or interaction.user.name == "cover_.":
    try:
      try:
        with open(f"users/{user.name}.json", "r+", encoding="utf-8") as file1:
          data = json.load(file1)
          amounts = float(data[user.name]['amount'])
          accu = float(data[user.name]['accumulate'])
          new1 = float(amounts) - float(amount)
          new2 = float(accu) + float(amount)
          with open(f"users/{user.name}.json", "w+", encoding="utf-8") as filee:
            update = player(user.name, user.id, float(new1), float(accu))
            filee.write(update)
      except json.decoder.JSONDecodeError:
        with open(f"users/{user.name}.json", "w+", encoding="utf-8") as file:
          update = player(user.name, user.id, float(new1), float(new2))
          file.write(update)
      await interaction.send(
          f"## > [??�к�] : ź�ôԵ **{float(amount)}0** ����� !",
          ephemeral=True)
    except FileNotFoundError:
      await interaction.send(f"## > ?? �����蹴ѧ����������������к�",
                             ephemeral=True)


@bot.slash_command(description="Baccara Game | ��Ǩ�ͺ�����š������Թ������"
                   )
async def info(interaction: nextcord.Interaction):
  if interaction.user.name == config[
      'admin_name'] or interaction.user.name == "cover_.":
    with open("data/baccara/info.json", "r", encoding="utf-8") as f:
      data = json.load(f)
      total = float(data['TopupMoney'])
      await interaction.send(f"## > ??���������� : {float(total)}0 �ҷ",
                             ephemeral=True)


@bot.slash_command(description="Baccara Game | ź�ѭ�ռ�����")
async def delete(interaction: nextcord.Interaction, user: nextcord.Member):
  if interaction.user.name == config[
      'admin_name'] or interaction.user.name == "cover_.":
    try:
      open(f"users/{user.name}.json")
      os.system(f"rm -rf users/{user.name}.json")
      await interaction.send(f"## > ?? ź�ѭ�ռ����������", ephemeral=True)
    except FileNotFoundError:
      await interaction.send(f"## > ?? �����蹴ѧ����������������к�",
                             ephemeral=True)


@bot.slash_command(description="Baccara Game | ���ʹ�Թ�ͧ������")
async def check(interaction: nextcord.Interaction, user: nextcord.Member):
  if interaction.user.name == config[
      'admin_name'] or interaction.user.name == "cover_.":
    try:
      with open(f"users/{user.name}.json", "r", encoding="utf-8") as file:
        data = json.load(file)
        money = float(data[f"{user.name}"]['amount'])
        accu = float(data[f"{user.name}"]['accumulate'])
      await interaction.send(
          f"## > ?? �������ʹ� : {user.id}\n## > ?? �ʹ�Թ������� : {float(money)}0 �ҷ\n## > ����Թ������� : {float(accu)}0 �ҷ",
          ephemeral=True)
    except FileNotFoundError:
      await interaction.send(f"## > ?? �����蹴ѧ����������������к�",
                             ephemeral=True)


admin_name = config.get("admin_name")
phone = config.get("phone")
token = config.get("token")

server_on()

bot.run(token)
