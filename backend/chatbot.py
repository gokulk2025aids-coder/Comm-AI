import os
import json
import re
import datetime
import random
import math
from database import Database

class Chatbot:
    def __init__(self):
        self.db = Database()
        self.api_key = os.getenv("GROQ_API_KEY") or os.getenv("ANTHROPIC_API_KEY") or os.getenv("OPENAI_API_KEY")
        self.api_type = "groq" if os.getenv("GROQ_API_KEY") else "anthropic" if os.getenv("ANTHROPIC_API_KEY") else "openai" if os.getenv("OPENAI_API_KEY") else "builtin"
        
        self.knowledge_base = {
            "general": {
                "greetings": ["Hello! How can I help you today?", "Hi there! What would you like to know?", "Greetings! I'm here to assist you."],
                "weather": "I don't have access to real-time weather data, but I recommend checking weather.com, AccuWeather, or your local weather app for current conditions.",
                "time": "I can tell you it's currently {time}, but for precise time zones, check worldclock.com or your device's clock.",
            },
            "email_types": {
                "professional": "Use formal language, clear subject lines, proper greetings (Dear/Hello), structured body, and professional closings (Best regards/Sincerely).",
                "apology": "Acknowledge the issue, express sincere regret, explain what happened, outline corrective actions, and offer compensation if appropriate.",
                "follow_up": "Reference previous communication, politely remind about pending items, provide context, and include a clear call-to-action.",
                "request": "Be clear and specific, explain why you need it, provide context, set reasonable deadlines, and express appreciation.",
                "complaint": "State the issue clearly, provide evidence, explain impact, request specific resolution, and maintain professional tone.",
                "meeting": "Propose specific times, state the purpose, list attendees, suggest duration, and request confirmation.",
                "thank_you": "Be specific about what you're thanking for, express genuine appreciation, mention impact, and maintain warmth."
            },
            "cultural_tips": {
                "japan": "Use indirect language, show humility, avoid direct refusals, use honorifics, be extremely polite, and build relationships slowly.",
                "india": "Show respect for hierarchy, use formal titles, be relationship-focused, allow time for rapport building, and be patient with decision-making.",
                "uk": "Use polite understatement, avoid being too direct, appreciate dry humor, maintain formality in business, and use 'please' and 'thank you' frequently.",
                "us": "Be direct and concise, focus on results, use friendly but professional tone, get to the point quickly, and emphasize efficiency.",
                "germany": "Be very direct, value punctuality, provide detailed information, separate personal and professional, and be formal until invited otherwise.",
                "brazil": "Build personal relationships first, be warm and expressive, allow flexibility with time, show enthusiasm, and use first names after introduction.",
                "spain": "Show warmth, build rapport, use formal usted for business, be expressive, and value personal connections.",
                "france": "Maintain formality, use vous in business, value eloquence, respect hierarchy, and be polite.",
                "china": "Respect hierarchy, build relationships, be patient, save face, and avoid direct confrontation.",
                "arabic": "Show respect, build trust first, be patient, relationship-focused, and use formal titles.",
                "russia": "Be formal in business, direct, detailed, use вы for formal communication, and build trust over time.",
                "tamil": "Show respect for elders and hierarchy, use honorifics, be polite and formal in business, and focus on building relationships."
            },
            "writing_tips": {
                "subject_line": "Keep it under 50 characters, be specific, include action words, avoid spam triggers, and make it scannable.",
                "structure": "Start with greeting, state purpose in first paragraph, provide details in body, end with clear call-to-action, and close professionally.",
                "tone": "Match recipient's formality level, be positive and solution-oriented, avoid jargon unless appropriate, and proofread carefully.",
                "best_practices": "Use active voice, keep paragraphs short, use bullet points for lists, respond within 24 hours, and always proofread."
            },
            "languages": {
                "translation": "CommAI supports translation between 13+ languages including English, Spanish, French, German, Italian, Portuguese, Dutch, Japanese, Chinese, Arabic, Hindi, Russian, and Tamil.",
                "detection": "Automatically detect the language of any email text to provide culturally appropriate analysis and suggestions.",
                "localized_tone": "Get tone analysis adjusted for cultural context - what's polite in one culture may be too formal or casual in another."
            }
        }
    
    def get_response(self, message, user_id, context=None):
        message_lower = message.lower()
        
        # Check if using external API
        if self.api_type == "groq":
            response = self._get_groq_response(message, context)
        elif self.api_type == "anthropic":
            response = self._get_anthropic_response(message, context)
        elif self.api_type == "openai":
            response = self._get_openai_response(message, context)
        else:
            response = self._get_builtin_response(message_lower, message, context)
        
        # Save to database
        self.db.save_chat(user_id, message, response)
        
        return response
    
    def _get_anthropic_response(self, message, context):
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)
            
            system_prompt = "You are a helpful AI assistant that can answer questions on any topic including email communication, science, technology, history, math, health, cooking, travel, entertainment, education, business, sports, philosophy, and general knowledge."
            
            messages = []
            if context:
                for item in context[-5:]:
                    messages.append({"role": "user", "content": item["message"]})
                    messages.append({"role": "assistant", "content": item["response"]})
            
            messages.append({"role": "user", "content": message})
            
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                system=system_prompt,
                messages=messages
            )
            
            return response.content[0].text
        except Exception as e:
            return self._get_builtin_response(message.lower(), message, context)
    
    def _get_openai_response(self, message, context):
        try:
            import openai
            openai.api_key = self.api_key
            
            messages = [{"role": "system", "content": "You are a helpful AI assistant that can answer questions on any topic."}]
            
            if context:
                for item in context[-5:]:
                    messages.append({"role": "user", "content": item["message"]})
                    messages.append({"role": "assistant", "content": item["response"]})
            
            messages.append({"role": "user", "content": message})
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=messages,
                max_tokens=1024
            )
            
            return response.choices[0].message.content
        except Exception as e:
            return self._get_builtin_response(message.lower(), message, context)
            
    def _get_groq_response(self, message, context):
        try:
            from openai import OpenAI
            client = OpenAI(
                api_key=self.api_key,
                base_url="https://api.groq.com/openai/v1",
            )
            
            messages = [{"role": "system", "content": "You are a helpful AI assistant that can answer questions on any topic."}]
            
            if context:
                for item in context[-5:]:
                    messages.append({"role": "user", "content": item["message"]})
                    messages.append({"role": "assistant", "content": item["response"]})
            
            messages.append({"role": "user", "content": message})
            
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                max_tokens=1024
            )
            
            return response.choices[0].message.content
        except Exception as e:
            return self._get_builtin_response(message.lower(), message, context)
    
    def _get_builtin_response(self, message_lower, original_message, context):
        # Simple greetings only
        if message_lower in ["hello", "hi", "hey", "greetings"]:
            return random.choice(self.knowledge_base["general"]["greetings"])
        
        # Advanced Math & Calculations
        if self._is_math_question(message_lower):
            return self._handle_advanced_math(message_lower, original_message)
        
        # Code Generation & Programming
        if self._is_code_request(message_lower):
            return self._generate_code(message_lower, original_message)
        
        # Creative Writing
        if self._is_creative_request(message_lower):
            return self._handle_creative_writing(message_lower, original_message)
        
        # Data Analysis & Explanations
        if self._is_analysis_request(message_lower):
            return self._handle_data_analysis(message_lower, original_message)
        
        # Problem Solving
        if self._is_problem_solving(message_lower):
            return self._handle_problem_solving(message_lower, original_message)
        
        # Language Translation & Learning
        if self._is_language_request(message_lower):
            return self._handle_language_tasks(message_lower, original_message)
        
        # Time queries
        if "what time" in message_lower or "current time" in message_lower:
            current_time = datetime.datetime.now().strftime("%H:%M:%S")
            return f"The current time is {current_time}. For precise time zones, check worldclock.com or your device's clock."
        
        # Weather queries
        if "weather" in message_lower:
            return self.knowledge_base["general"]["weather"]
        
        # Comprehensive Knowledge Base
        response = self._handle_comprehensive_knowledge(message_lower, original_message)
        if response:
            return response
        
        # Email-specific queries (existing functionality)
        if "professional email" in message_lower or "business email" in message_lower:
            return self._format_response("Professional Email Writing", self.knowledge_base["email_types"]["professional"])
        
        if "apology" in message_lower and "email" in message_lower:
            return self._format_response("Apology Email", self.knowledge_base["email_types"]["apology"])
        
        if "follow" in message_lower and "up" in message_lower:
            return self._format_response("Follow-up Email", self.knowledge_base["email_types"]["follow_up"])
        
        # Try to answer any other question intelligently
        return self._try_answer_question(message_lower, original_message)
    
    def _is_math_question(self, message):
        math_keywords = ["+", "-", "*", "/", "calculate", "math", "plus", "minus", "multiply", "divide", 
                        "square root", "sqrt", "power", "^", "factorial", "sin", "cos", "tan", "log", "ln"]
        return any(keyword in message for keyword in math_keywords)
    
    def _handle_advanced_math(self, message_lower, original_message):
        try:
            # Extract numbers
            numbers = re.findall(r'-?\d+(?:\.\d+)?', original_message)
            
            # Basic arithmetic
            if len(numbers) >= 2:
                num1, num2 = float(numbers[0]), float(numbers[1])
                
                if "+" in message_lower or "plus" in message_lower or "add" in message_lower:
                    return f"The result is: {num1 + num2}"
                elif "-" in message_lower or "minus" in message_lower or "subtract" in message_lower:
                    return f"The result is: {num1 - num2}"
                elif "*" in message_lower or "multiply" in message_lower or "times" in message_lower:
                    return f"The result is: {num1 * num2}"
                elif "/" in message_lower or "divide" in message_lower:
                    if num2 != 0:
                        return f"The result is: {num1 / num2}"
                    else:
                        return "Cannot divide by zero!"
                elif "power" in message_lower or "^" in message_lower:
                    return f"The result is: {num1 ** num2}"
            
            # Advanced functions
            if len(numbers) >= 1:
                num = float(numbers[0])
                
                if "square root" in message_lower or "sqrt" in message_lower:
                    if num >= 0:
                        return f"The square root of {num} is: {math.sqrt(num)}"
                    else:
                        return "Cannot calculate square root of negative number!"
                
                if "factorial" in message_lower and num >= 0 and num == int(num):
                    return f"The factorial of {int(num)} is: {math.factorial(int(num))}"
                
                if "sin" in message_lower:
                    return f"sin({num}) = {math.sin(math.radians(num))}"
                if "cos" in message_lower:
                    return f"cos({num}) = {math.cos(math.radians(num))}"
                if "tan" in message_lower:
                    return f"tan({num}) = {math.tan(math.radians(num))}"
                if "log" in message_lower:
                    if num > 0:
                        return f"log({num}) = {math.log10(num)}"
                    else:
                        return "Cannot calculate logarithm of non-positive number!"
            
            return "I can help with advanced math! Try: addition, subtraction, multiplication, division, square root, factorial, trigonometry (sin, cos, tan), logarithms, and more."
        except:
            return "I can help with advanced math calculations. Please provide valid numbers and operations."
    
    def _is_code_request(self, message):
        code_keywords = ["write code", "create function", "python code", "javascript code", "html", "css", 
                        "algorithm", "program", "script", "function", "class", "method", "code example"]
        return any(keyword in message for keyword in code_keywords)
    
    def _generate_code(self, message_lower, original_message):
        if "python" in message_lower:
            if "function" in message_lower:
                return """Here's a Python function example:

```python
def example_function(parameter):
    \"\"\"
    This is a sample function
    \"\"\"
    result = parameter * 2
    return result

# Usage
output = example_function(5)
print(output)  # Output: 10
```

What specific Python function would you like me to create?"""
            
            elif "calculator" in message_lower:
                return """Here's a Python calculator:

```python
def calculator():
    while True:
        try:
            num1 = float(input("Enter first number: "))
            operator = input("Enter operator (+, -, *, /): ")
            num2 = float(input("Enter second number: "))
            
            if operator == '+':
                result = num1 + num2
            elif operator == '-':
                result = num1 - num2
            elif operator == '*':
                result = num1 * num2
            elif operator == '/':
                result = num1 / num2 if num2 != 0 else "Cannot divide by zero"
            else:
                result = "Invalid operator"
            
            print(f"Result: {result}")
            
            if input("Continue? (y/n): ").lower() != 'y':
                break
        except ValueError:
            print("Invalid input!")

calculator()
```"""
        
        elif "javascript" in message_lower:
            return """Here's a JavaScript example:

```javascript
// Function example
function greetUser(name) {
    return `Hello, ${name}! Welcome to our website.`;
}

// Usage
const message = greetUser("John");
console.log(message);

// Arrow function version
const greetUserArrow = (name) => `Hello, ${name}! Welcome to our website.`;
```

What specific JavaScript code would you like me to create?"""
        
        elif "html" in message_lower:
            return """Here's an HTML template:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Website</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .container { max-width: 800px; margin: 0 auto; }
        .header { background: #333; color: white; padding: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Welcome to My Website</h1>
        </div>
        <main>
            <p>This is the main content area.</p>
        </main>
    </div>
</body>
</html>
```"""
        
        return "I can generate code in Python, JavaScript, HTML, CSS, and more! What specific code would you like me to create?"
    
    def _is_creative_request(self, message):
        creative_keywords = ["write story", "create poem", "write poem", "story about", "poem about", 
                           "creative writing", "write essay", "write article", "write blog"]
        return any(keyword in message for keyword in creative_keywords)
    
    def _handle_creative_writing(self, message_lower, original_message):
        if "story" in message_lower:
            return """Here's a short story for you:

**The Digital Garden**

Sarah discovered the old laptop in her grandmother's attic, its screen flickering with an unusual blue glow. When she opened it, instead of a desktop, she found a beautiful digital garden with pixelated flowers that seemed to dance in the virtual breeze.

Each click made the flowers bloom brighter, and soon she realized that her grandmother had been cultivating this secret world for years, leaving behind a legacy of digital beauty that would live forever in the cloud.

The garden became Sarah's sanctuary, a place where technology and nature merged in perfect harmony.

Would you like me to write a story on a specific topic?"""
        
        elif "poem" in message_lower:
            return """Here's a poem for you:

**Digital Dreams**

In circuits bright and screens aglow,
Where data streams like rivers flow,
We find our modern hearts can beat
In rhythm with the tech we meet.

The future calls through fiber lines,
Where human soul with silicon shines,
And in this dance of old and new,
We discover what it means to be true.

Would you like me to write a poem on a specific theme?"""
        
        elif "essay" in message_lower or "article" in message_lower:
            return """Here's an essay outline on "The Impact of Technology on Communication":

**Introduction:**
- Technology has revolutionized how we communicate
- From letters to instant messaging and video calls

**Body Paragraphs:**
1. **Speed and Accessibility**
   - Instant global communication
   - Breaking down geographical barriers

2. **New Forms of Expression**
   - Emojis, memes, and digital language
   - Visual communication through images and videos

3. **Challenges and Concerns**
   - Digital divide and accessibility issues
   - Loss of face-to-face interaction skills

**Conclusion:**
- Technology as a tool that enhances human connection
- The importance of balanced communication approaches

Would you like me to develop any specific section or write about a different topic?"""
        
        return "I can help with creative writing! I can write stories, poems, essays, articles, and more. What would you like me to create?"
    
    def _is_analysis_request(self, message):
        analysis_keywords = ["analyze", "explain", "compare", "contrast", "pros and cons", 
                           "advantages", "disadvantages", "evaluate", "assess"]
        return any(keyword in message for keyword in analysis_keywords)
    
    def _handle_data_analysis(self, message_lower, original_message):
        if "pros and cons" in message_lower or "advantages" in message_lower:
            if "remote work" in message_lower:
                return """**Remote Work Analysis:**

**Pros:**
✅ Flexible schedule and work-life balance
✅ No commuting time or costs
✅ Access to global job opportunities
✅ Comfortable work environment
✅ Increased productivity for many people
✅ Cost savings on office attire and meals

**Cons:**
❌ Potential isolation and loneliness
❌ Difficulty separating work and personal life
❌ Communication challenges with team
❌ Distractions at home
❌ Limited career networking opportunities
❌ Technology dependency and issues

**Conclusion:** Remote work offers significant flexibility but requires strong self-discipline and communication skills."""
            
            elif "social media" in message_lower:
                return """**Social Media Analysis:**

**Pros:**
✅ Global connectivity and communication
✅ Information sharing and awareness
✅ Business and marketing opportunities
✅ Creative expression platform
✅ Community building and support groups
✅ Educational content and learning

**Cons:**
❌ Privacy and data security concerns
❌ Cyberbullying and online harassment
❌ Addiction and time consumption
❌ Misinformation spread
❌ Mental health impacts (comparison, FOMO)
❌ Echo chambers and polarization

**Conclusion:** Social media is a powerful tool that requires mindful and responsible usage."""
        
        return "I can analyze various topics! Please specify what you'd like me to analyze - technology, business concepts, social issues, etc."
    
    def _is_problem_solving(self, message):
        problem_keywords = ["how to solve", "problem with", "issue with", "help me fix", 
                          "troubleshoot", "solution for", "resolve", "fix"]
        return any(keyword in message for keyword in problem_keywords)
    
    def _handle_problem_solving(self, message_lower, original_message):
        if "computer" in message_lower or "laptop" in message_lower:
            return """**Computer Troubleshooting Steps:**

1. **Restart your computer** - Solves 80% of issues
2. **Check connections** - Ensure all cables are secure
3. **Update software** - Keep OS and drivers current
4. **Run antivirus scan** - Check for malware
5. **Free up disk space** - Delete unnecessary files
6. **Check for overheating** - Clean dust from vents
7. **Safe mode** - Boot in safe mode to isolate issues

**Common Issues:**
- Slow performance → Close unnecessary programs, add RAM
- Won't start → Check power supply, try safe mode
- Internet issues → Restart router, check network settings
- Blue screen → Update drivers, check hardware

What specific computer issue are you experiencing?"""
        
        elif "time management" in message_lower:
            return """**Time Management Solutions:**

**The Pomodoro Technique:**
1. Work for 25 minutes focused
2. Take 5-minute break
3. Repeat 4 cycles
4. Take longer 15-30 minute break

**Priority Matrix:**
- **Urgent + Important** → Do first
- **Important + Not Urgent** → Schedule
- **Urgent + Not Important** → Delegate
- **Not Urgent + Not Important** → Eliminate

**Daily Planning:**
1. List all tasks
2. Prioritize by importance
3. Time-block your calendar
4. Include buffer time
5. Review and adjust

**Tools:** Calendars, task apps, timers, notebooks

What specific time management challenge are you facing?"""
        
        return "I can help solve various problems! Please describe the specific issue you're facing - technical, personal, work-related, etc."
    
    def _is_language_request(self, message):
        language_keywords = ["translate", "translation", "learn language", "speak", "grammar", 
                           "vocabulary", "pronunciation", "language learning"]
        return any(keyword in message for keyword in language_keywords)
    
    def _handle_language_tasks(self, message_lower, original_message):
        if "translate" in message_lower:
            return """**Translation Services:**

I can help with basic translations between major languages:
- English ↔ Spanish, French, German, Italian
- English ↔ Portuguese, Dutch, Russian
- English ↔ Japanese, Chinese, Arabic, Hindi

**Example Translations:**
- Hello → Hola (Spanish), Bonjour (French), Hallo (German)
- Thank you → Gracias (Spanish), Merci (French), Danke (German)
- Good morning → Buenos días (Spanish), Bonjour (French), Guten Morgen (German)

What would you like me to translate?"""
        
        elif "learn" in message_lower and "language" in message_lower:
            return """**Language Learning Tips:**

**For Beginners:**
1. **Start with basics** - Greetings, numbers, common phrases
2. **Daily practice** - 15-30 minutes consistently
3. **Use apps** - Duolingo, Babbel, Rosetta Stone
4. **Immersion** - Watch movies, listen to music
5. **Practice speaking** - Find language exchange partners

**Effective Methods:**
- **Spaced repetition** for vocabulary
- **Grammar in context** rather than rules
- **Real conversations** with native speakers
- **Cultural learning** alongside language

**Resources:**
- Language learning apps
- YouTube channels
- Podcasts for listening practice
- Online tutors and conversation partners

Which language are you interested in learning?"""
        
        return "I can help with translations, language learning tips, grammar explanations, and vocabulary building. What language assistance do you need?"
    
    def _handle_comprehensive_knowledge(self, message_lower, original_message):
        # Science & Technology
        if "quantum" in message_lower:
            return "Quantum physics deals with the behavior of matter and energy at the atomic and subatomic level. Key concepts include superposition (particles existing in multiple states), entanglement (particles being connected across distances), and uncertainty principle (cannot precisely know both position and momentum). Applications include quantum computing, cryptography, and teleportation."
        
        if "blockchain" in message_lower:
            return "Blockchain is a distributed ledger technology that maintains a continuously growing list of records (blocks) linked and secured using cryptography. Each block contains a hash of the previous block, timestamp, and transaction data. It's decentralized, transparent, and immutable, making it useful for cryptocurrencies, supply chain tracking, and smart contracts."
        
        if "machine learning" in message_lower or "ml" in message_lower:
            return "Machine Learning is a subset of AI that enables computers to learn and improve from experience without being explicitly programmed. Types include supervised learning (labeled data), unsupervised learning (pattern finding), and reinforcement learning (reward-based). Applications: image recognition, natural language processing, recommendation systems, autonomous vehicles."
        
        # History & Culture
        if "renaissance" in message_lower:
            return "The Renaissance (14th-17th centuries) was a period of cultural rebirth in Europe, marking the transition from medieval to modern times. Key features: renewed interest in classical learning, humanism, artistic innovation (Leonardo da Vinci, Michelangelo), scientific revolution (Galileo, Copernicus), and exploration (Columbus, Magellan). It began in Italy and spread throughout Europe."
        
        if "world war" in message_lower:
            return "World War I (1914-1918) was triggered by the assassination of Archduke Franz Ferdinand, involving complex alliances. Major battles: Somme, Verdun, Gallipoli. Ended with Treaty of Versailles. World War II (1939-1945) began with Germany's invasion of Poland, involving Axis vs. Allied powers. Key events: Holocaust, Pearl Harbor, D-Day, atomic bombs. Both wars reshaped global politics."
        
        # Health & Medicine
        if "nutrition" in message_lower or "diet" in message_lower:
            return "Balanced nutrition includes: **Macronutrients** - Carbohydrates (45-65% calories), Proteins (10-35%), Fats (20-35%). **Micronutrients** - Vitamins and minerals. **Guidelines**: Eat variety of fruits/vegetables, whole grains, lean proteins, healthy fats. Limit processed foods, added sugars, excessive sodium. Stay hydrated. Consult healthcare providers for personalized advice."
        
        if "exercise" in message_lower or "fitness" in message_lower:
            return "**Exercise Guidelines**: 150 minutes moderate aerobic activity weekly + 2 days strength training. **Types**: Cardio (running, cycling), Strength (weights, resistance), Flexibility (yoga, stretching), Balance (tai chi). **Benefits**: Improved cardiovascular health, stronger muscles/bones, better mental health, weight management. Start gradually, listen to your body, stay consistent."
        
        # Business & Economics
        if "cryptocurrency" in message_lower or "bitcoin" in message_lower:
            return "Cryptocurrency is digital/virtual currency secured by cryptography, making it nearly impossible to counterfeit. **Bitcoin** (2009) was the first decentralized cryptocurrency using blockchain technology. **Features**: Decentralized, limited supply, transparent transactions, volatile prices. **Uses**: Digital payments, store of value, investment. **Risks**: Price volatility, regulatory uncertainty, security concerns."
        
        if "startup" in message_lower or "entrepreneur" in message_lower:
            return "**Startup Essentials**: 1) **Validate idea** - Market research, customer feedback 2) **Business plan** - Model, target market, financials 3) **MVP** - Minimum viable product 4) **Funding** - Bootstrapping, investors, loans 5) **Team** - Co-founders, key hires 6) **Legal** - Business structure, IP protection 7) **Marketing** - Brand, customer acquisition. Key: Solve real problems, iterate quickly, focus on customers."
        
        return None
    
    def _try_answer_question(self, message_lower, original_message):
        # Look for question patterns and try to provide helpful answers
        if "what is" in message_lower or "tell me about" in message_lower or "explain" in message_lower:
            return "I'd be happy to help explain that topic! Could you be more specific about what you'd like to know? I can provide detailed information on science, technology, history, health, business, and many other subjects."
        elif "how to" in message_lower or "how do" in message_lower:
            return "I can provide step-by-step instructions and guidance on various topics. Could you specify what you'd like to learn how to do? I can help with technical tasks, learning new skills, problem-solving, and much more."
        elif "why" in message_lower:
            return "That's a great question! I can help explain the reasons behind various phenomena, decisions, or concepts. Could you provide more details about what you'd like to understand?"
        elif "when" in message_lower:
            return "I can help with timing, historical dates, and scheduling information. What specific timing or date information are you looking for?"
        elif "where" in message_lower:
            return "I can provide location information, travel guidance, and geographical details. What location or place are you asking about?"
        else:
            return """🤖 **Advanced AI Assistant** - I can help you with:

🧮 **Advanced Math** - Calculus, trigonometry, statistics, complex calculations
💻 **Code Generation** - Python, JavaScript, HTML, CSS, algorithms, debugging
✍️ **Creative Writing** - Stories, poems, essays, articles, content creation
📊 **Data Analysis** - Compare options, pros/cons, research insights
🔧 **Problem Solving** - Technical issues, life challenges, troubleshooting
🌍 **Language Services** - Translation, learning tips, grammar help
🔬 **Science & Tech** - Physics, chemistry, AI, blockchain, quantum computing
📚 **Education** - Explanations, study guides, learning strategies
💼 **Business** - Startups, marketing, finance, professional development
🏥 **Health & Wellness** - Nutrition, exercise, mental health (general info)
🎯 **Goal Achievement** - Planning, time management, productivity
📧 **Email Communication** - Professional writing, cultural tips

Just ask me anything! I provide detailed, helpful responses on virtually any topic."""
    
    def _format_response(self, title, content):
        return f"**{title}**\n\n{content}"
    
    def get_chat_history(self, user_id):
        return self.db.get_chat_history(user_id)