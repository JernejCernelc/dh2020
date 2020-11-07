const express = require('express')
const path = require('path')
const { Sequelize, DataTypes, Model, Op } = require('sequelize');
var _ = require('lodash');



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
        title: { type: DataTypes.TEXT, allowNull: false },
        content: { type: DataTypes.TEXT, allowNull: true },
        topic: { type: DataTypes.TEXT, allowNull: false },
        datetime: { type: DataTypes.DATE, allowNull: false },
        link: { type: DataTypes.TEXT, allowNull: false, unique: true },
        score: { type: DataTypes.FLOAT },
    }, {
        sequelize,
        timestamps: false,
        tableName: "news_article"
    });

    /* sync model to db */
    await sequelize.sync({ force: false });
    console.log("All models were synchronized successfully.");

}

/////////
// DAO
/////////
async function findArticlesForTopic(myTopic) {

    const articles = await NewsArticle.findAll({
        where: {
            topic: {
                [Op.eq]: myTopic
            }
        }
    });

    // Group articles by day
    const articlesByDate = _.groupBy(articles, (article) =>
        `${article.datetime.getDate()}/${article.datetime.getMonth()}/${article.datetime.getFullYear()}`
    )

    // Sort dates
    const sortedDates = Object.keys(articlesByDate).sort()

    // Nest articles under corresponding date
    return _.map(sortedDates, (date) => {
        return {
            datetime: date,
            news: _.sortBy(articlesByDate[date], (article) => article.datetime)
        }
    })
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