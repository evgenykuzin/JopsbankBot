import models
import bot

if __name__ == '__main__':
    models.initialize_db()
    bot.run()