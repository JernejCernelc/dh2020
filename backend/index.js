const express = require('express')
const path = require('path')
const { Sequelize, DataTypes, Model, Op } = require('sequelize');




class NewsArticle extends Model { }


async function initDb() {
  const sequelize = new Sequelize('sqlite:../data/news.db')
  try {
    await sequelize.authenticate();
    console.log('Connection has been established successfully.');
  } catch (error) {
    console.error('Unable to connect to the database:', error);
  }

  /* model definition */
  NewsArticle.init({
    title: { type: DataTypes.STRING, allowNull: false },
    topic: { type: DataTypes.STRING, allowNull: false },
    datetime: { type: DataTypes.STRING, allowNull: false },
    link: { type: DataTypes.STRING, allowNull: false },
  }, {
    sequelize,
    timestamps: false,
    tableName: "news_article"
  });

  /* sync model to db */
  await sequelize.sync({ force: true });
  console.log("All models were synchronized successfully.");


  /* some dummy data */
  await NewsArticle.create({
    title: "Very cool title 1",
    topic: "covid-19",
    datetime: "07/11/2020 15:00",
    link: "https://example.com/",
  });
  await NewsArticle.create({
    title: "Very cool title 2",
    topic: "covid-19",
    datetime: "07/11/2020 15:00",
    link: "https://example.com/",
  });
  await NewsArticle.create({
    title: "Very cool title 3",
    topic: "covid-19",
    datetime: "08/11/2020 15:00",
    link: "https://example.com/",
  });

  await NewsArticle.create({
    title: "Biden",
    topic: "volitve zda",
    datetime: "07/11/2020 15:00",
    link: "https://example.com/",
  });
  await NewsArticle.create({
    title: "Biden",
    topic: "volitve zda",
    datetime: "07/11/2020 15:00",
    link: "https://example.com/",
  });
  await NewsArticle.create({
    title: "Biden",
    topic: "volitve zda",
    datetime: "07/11/2020 15:00",
    link: "https://example.com/",
  });


}

/* DAOOOO */
async function findArticlesForTopic(myTopic) {

  const articles = await NewsArticle.findAll({
    where: {
      topic: {
        [Op.eq]: myTopic
      }
    }
  });

  console.log("Got " + articles.length + " results for topic " + myTopic + ".");
  return articles;
}




/* public static void main(String[] args) */
(async () => {

  await initDb();

  /* server */
  const app = express()
  const port = 8080

  app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname + '/index.html'));
  });

  app.get('/timeline/:topic', async (req, res) => {
    const topic = req.params.topic;

    const articles = await findArticlesForTopic(topic);
    res.json({
      "topic": topic,
      "dates": articles
    });
  });

  app.listen(port, () => {
    console.log(`Server listening at http://localhost:${port}`)
  });

})();