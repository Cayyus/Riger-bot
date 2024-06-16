from discord import Interaction, app_commands, Embed, Button, ButtonStyle
from discord.app_commands import Choice
from discord.ui import View, button
from discord.ext import commands

from utils.db.db_config import UserDB
from utils.formatters import trivia_categories

import httpx
import base64
import random
from ratelimit import limits, sleep_and_retry

R_LIMITS = 1
R_PERIOD = 5

categories = [Choice(name=category['name'], value=category['value']) for category in trivia_categories]
difficulties = [
    Choice(name='Random difficulty', value='random'),
    Choice(name='Easy', value='easy'),
    Choice(name='Medium', value='medium'),
    Choice(name='Hard', value='hard')
]
types = [
    Choice(name='True/False', value='boolean'),
    Choice(name='Multiple Choice Questions', value='multiple')
]


class SharedChoiceMenu(View):
    def __init__(self, questions, user, db, current_index=0, score=0, credits_earned=0, credits_lost=0):
        super().__init__(timeout=60) 
        self.questions = questions
        self.user = user
        self.db = db
        self.current_index = current_index
        self.score = score
        self.credits_earned = credits_earned
        self.credits_lost = credits_lost
        self.current_question = questions[current_index]
        self.correct_ans = self.current_question['correct_answer']
        self.options = self.current_question['all_answers']
        self.message = None
    
    async def handle_interaction(self, interaction: Interaction, selected_option: str):
        if interaction.user.name != self.user:
            await interaction.response.send_message("You cannot play this, please do your own trivia.", ephemeral=True)
        else:
            if selected_option == self.correct_ans:
                self.score += 1
                self.credits_earned += 10
                await interaction.response.send_message(f"Correct! Answer chosen: **{selected_option}**")
                self.db.update_coin_count(amount=10, type="+")
            else:
                self.credits_lost += 5
                await interaction.response.send_message(f"Incorrect! The correct answer was: **{self.correct_ans}**, Answer chosen: **{selected_option}**")
                self.db.update_coin_count(amount=5, type="-")
            
            self.current_index += 1
            if self.current_index < len(self.questions):
                self.current_question = self.questions[self.current_index]
                self.correct_ans = self.current_question['correct_answer']
                self.options = self.current_question['all_answers']
                embed = self.create_embed()
                await interaction.followup.send(embed=embed, view=self)
            else:
                embed = Embed(title="Results")
                embed.description = f"""Your score was {self.score}/{len(self.questions)} ({format(self.score/len(self.questions)*100, '.2f')}%)\n
                You gained {self.credits_earned} credits.\n
                You lost {self.credits_lost} credits.\n
                Your account balance is {self.db.select_user()[0][3]} credits.
                """
                await interaction.followup.send(embed=embed)
                self.stop()

    def create_embed(self):
        qs_name = self.current_question['question']
        qs_cat = self.current_question['category']
        qs_difficulty = self.current_question['difficulty']
        options = "\n".join(f":number_{i+1}: {ans}" for i, ans in enumerate(self.options))
        embed = Embed(title=qs_name, description=options)
        embed.set_footer(text=f"Category: {qs_cat}, Difficulty: {qs_difficulty}")
        return embed
    
    async def on_timeout(self):
        if self.message:
            await self.message.edit(view=self)
            await self.message.channel.send("Timeout elapsed. Trivia stopped.")


class MultipleChoiceMenu(SharedChoiceMenu):
    def __init__(self, questions, user, db, current_index=0, score=0, credits_earned=0, credits_lost=0):
        super().__init__(questions, user, db, current_index, score, credits_earned, credits_lost)
    
    @button(emoji="1️⃣")
    async def one_callback(self, interaction: Interaction, button: Button):
        await self.handle_interaction(interaction, self.options[0])

    @button(emoji="2️⃣")
    async def two_callback(self, interaction: Interaction, button: Button):
        await self.handle_interaction(interaction, self.options[1])

    @button(emoji="3️⃣")
    async def three_callback(self, interaction: Interaction, button: Button):
        await self.handle_interaction(interaction, self.options[2])

    @button(emoji="4️⃣")
    async def four_callback(self, interaction: Interaction, button: Button):
        await self.handle_interaction(interaction, self.options[3])


class BooleanMenu(SharedChoiceMenu):
    def __init__(self, questions, user, db, current_index=0, score=0, credits_earned=0, credits_lost=0):
        super().__init__(questions, user, db, current_index, score, credits_earned, credits_lost)

    def create_embed(self):
        qs_name = self.current_question['question']
        qs_cat = self.current_question['category']
        qs_difficulty = self.current_question['difficulty']
        embed = Embed(title=qs_name)
        embed.set_footer(text=f"Category: {qs_cat}, Difficulty: {qs_difficulty}")
        return embed
    
    @button(label='True', style=ButtonStyle.green)
    async def true_callback(self, interaction: Interaction, button: Button):
        await self.handle_interaction(interaction, "True")

    @button(label='False', style=ButtonStyle.red)
    async def false_callback(self, interaction: Interaction, button: Button):
        await self.handle_interaction(interaction, "False")


class TriviaCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    def construct_url(self, amount, cat, difficulty, type):
        url = f'https://opentdb.com/api.php?amount={amount}&encode=base64'
        if cat != 'random':
            url += f'&category={cat}'
        if difficulty != 'random':
            url += f'&difficulty={difficulty}'
        url += f'&type={type}'
        return url

    @sleep_and_retry
    @limits(calls=R_LIMITS, period=R_PERIOD)
    def get_questions(self, amount, cat, difficulty, type) -> dict:
        url = self.construct_url(amount, cat, difficulty, type)

        response = httpx.get(url)
        response_code = response.json()['response_code']

        if response_code == 0:
            return {'results': response.json()['results']}, 200
        elif response_code == 1:
            return False, 204
        else:
            return False, response.status_code
    
    def parse_questions(self, result, q_type) -> list:
        questions = []

        for question in result:
            qs_name = base64.b64decode(question['question']).decode('utf-8')
            qs_cat = base64.b64decode(question['category']).decode('utf-8')
            qs_difficulty = base64.b64decode(question['difficulty']).decode('utf-8')

            correct_answer = base64.b64decode(question['correct_answer']).decode('utf-8')
            all_answers = [base64.b64decode(ans).decode('utf-8') for ans in question['incorrect_answers']]
            all_answers.append(correct_answer)
            random.shuffle(all_answers)
        
            questions.append({
                'question': qs_name,
                "category": qs_cat,
                "difficulty": qs_difficulty,
                'correct_answer': correct_answer,
                'all_answers': all_answers
            })
        
        return questions
        
    @app_commands.command(name='trivia', description='Quiz yourself on a variety of categories!')
    @app_commands.describe(amount="Choose the number of questions you want to answer, must be above 5 but below 50", category='Choose a category of questions', difficulty='Choose the difficulty level', type='Choose the type of questions')
    @app_commands.choices(category=categories, difficulty=difficulties, type=types)
    async def trivia(self, interaction: Interaction, amount: int, category: Choice[str], difficulty: Choice[str], type: Choice[str]):
        await interaction.response.defer()
        user = interaction.user.name
        db = UserDB(interaction.user.name, interaction.user.id)
        db_user = db.select_user()

        if db_user:
            name = db.get_username()
            
            if name != interaction.user.name:
                db.update_username()
        else:
            db.insert_user()
            
        if amount < 5 or amount > 50:
            await interaction.followup.send("Too little or too many questions requested, please request between 5-50 questions.")
            return 
        
        resp, status_code = self.get_questions(amount=amount, cat=category.value, difficulty=difficulty.value, type=type.value)
        
        if resp and status_code == 200: #everything is successful
            result = resp['results']
            typ = base64.b64decode(result[0]['type']).decode('utf-8')

            questions = self.parse_questions(result, typ)
            if typ == "multiple":
                embed = Embed(title=questions[0]['question'], description="\n".join(f":number_{i+1}: {ans}" for i, ans in enumerate(questions[0]['all_answers'])))
            else:
                embed = Embed(title=questions[0]['question'])
            
            embed.set_footer(text=f'Category: {questions[0]["category"]}, Difficulty: {questions[0]["difficulty"]}')
            
            if typ == "multiple":
                menu = MultipleChoiceMenu(questions, user, db)
            else:
                menu = BooleanMenu(questions, user, db)
            
            message = await interaction.followup.send(embed=embed, view=menu)
            menu.message = message 

        elif status_code == 204: #not enough questions
            await interaction.followup.send("Not enough questions for this category/difficulty/type. Consider tweaking the parameters such as changing the category/difficulty/type or reducing the number of questions, or if you picked randomly, try again with the same options.")
        
        elif resp is False and status_code != 204: #response is errored but its not question availability
            await interaction.followup.send("An error occurred, try again.")
            print(resp, "\n\n", status_code)
                                    

async def setup(bot): 
    await bot.add_cog(TriviaCog(bot))
