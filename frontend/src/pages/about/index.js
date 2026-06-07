import { Container, Main } from '../../components'
import styles from './styles.module.css'
import MetaTags from 'react-meta-tags'

const About = ({ updateOrders, orders }) => {
  
  return <Main>
    <MetaTags>
      <title>О проекте</title>
      <meta name="description" content="Фудграм - О проекте" />
      <meta property="og:title" content="О проекте" />
    </MetaTags>
    
    <Container>
      <h1 className={styles.title}>Привет!</h1>
      <div className={styles.content}>
        <div>
          <h2 className={styles.subtitle}>Это Foodgram — приложение для тех, кто любит готовить.</h2>
          <div className={styles.text}>
            <p className={styles.textItem}>
              Здесь можно публиковать рецепты, добавлять ингредиенты и время приготовления, сохранять блюда в избранное, подписываться на авторов и скачивать список продуктов для выбранных рецептов.
            </p>
            <p className={styles.textItem}>
              Проект был разработан в рамках обучения backend-разработке, но доработан и развёрнут как полноценное веб-приложение: с API, авторизацией, базой данных, контейнеризацией и публикацией на сервере.
            </p>
            <p className={styles.textItem}>
              Основная цель проекта — показать полный цикл разработки backend-приложения: от проектирования моделей и API до деплоя, настройки веб-сервера и подготовки проекта к работе в сети.
            </p>
            <p className={styles.textItem}>
              Если вы читаете это, значит, у меня всё получилось! Буду рад сотрудничеству. <a href="https://vk.com/mafakkafox" className={styles.textLink}>Мой ВК</a>
            </p>
          </div>
        </div>
        <aside>
          <h2 className={styles.additionalTitle}>
            Ссылки
          </h2>
          <div className={styles.text}>
            <p className={styles.textItem}>
              Код проекта находится тут - <a href="https://github.com/IhuliR/foodgram" className={styles.textLink}>Github</a>
            </p>
            <p className={styles.textItem}>
              Автор проекта: <a href="https://github.com/IhuliR" className={styles.textLink}>Илья Рощин</a>
            </p>
            <p className={styles.textItem}>
              А ещё я написал книгу, лол: <a href="https://eksmo.ru/ebook/ty-ITDA34972/" className={styles.textLink}>Её уже не купить, если интересно, свяжитесь со мной</a>
            </p>
          </div>
        </aside>
      </div>
      
    </Container>
  </Main>
}

export default About

