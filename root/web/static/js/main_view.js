const tg = window.Telegram.WebApp;
const tg_id = tg.initDataUnsafe.user.id;

document.body.style.overflow = "hidden";

const currentDate = new Date();
const day = String(currentDate.getDate()).padStart(2, "0");
const month = String(currentDate.getMonth() + 1).padStart(2, "0");
const year = currentDate.getFullYear();

const formattedDate = `${day}.${month}.${year}`;
document.querySelector(".date").textContent = `${formattedDate} — сегодня`;

async function sendData(link) {
  const request = await fetch(`..${link}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ tg_id: tg_id }),
  });
  const response = await request.json();
  return response;
}

let diameter = 0;
let nutrientStreak = {};
let gender = "";
let genderTextEaten = "";
let genderTextNotEaten = "";
let promises = [];

async function setPlateImage(className, plate, index) {
  console.log("setPlateImage");
  let imagePath = "";
  if (plate.percentages[0] === "100") {
    imagePath = "../static/images/1-part.png";
  } else if (plate.percentages[0] === "50" && plate.percentages.length === 2) {
    imagePath = "../static/images/2-parts.png";
  } else if (plate.percentages[0] === "33") {
    imagePath = "../static/images/3-33-parts.png";
  } else if (plate.percentages.length === 4) {
    imagePath = "../static/images/4-parts.png";
  } else {
    imagePath = "../static/images/3-parts.png";
  }

  let img = new Image();
  let imgLoaded = new Promise((resolve, reject) => {
    img.onload = resolve;
    img.onerror = reject;
  });
  img.src = imagePath;
  img.className = "card__plate";
  document.querySelector(`.${className}${index + 1}`).appendChild(img);
  document
    .querySelector(`.${className}${index + 1}`)
    .insertAdjacentElement("afterbegin", img);

  return imgLoaded;
}

function formatNumber(num) {
  if (Number.isInteger(num)) {
    return num.toString();
  } else {
    return parseFloat(num.toFixed(2)).toString();
  }
}

function setPlateStars(className, plate, index) {
  const cardStarsElement = document.querySelector(`.${className}${index + 1}`);
  const greenStarImage = '<img src="../static/images/green-star.svg" alt="" />';
  const grayStarImage = '<img src="../static/images/gray-star.svg" alt="" />';

  for (let i = 1; i < 6; i++) {
    const starImage =
      i <= plate.recipe_difficulty ? greenStarImage : grayStarImage;
    cardStarsElement.insertAdjacentHTML("beforeend", starImage);
  }
}

async function setUserParameters() {
  const userParameters = await sendData("/api/get_user_parameters");
  diameter = userParameters.plate_diameter;
  gender = userParameters.gender;
  genderTextEaten = gender === "Мужской" ? "Я съел" : "Я съела";
  genderTextNotEaten = gender === "Мужской" ? "Я не съел" : "Я не съела";
  document.querySelector(".i_have_eaten").textContent = genderTextEaten;
  document.querySelector(".coin__amount").textContent = userParameters.balance;
  document.querySelector(".weight-value").textContent = `${formatNumber(
    userParameters.weight
  )} кг`;
  document.querySelector(".height-value").textContent = `${formatNumber(
    userParameters.height
  )} см`;
  document.querySelector(".age-value").textContent = formatNumber(
    userParameters.age
  );

  document.querySelectorAll(".plate-diameter-value").forEach((el) => {
    el.textContent = `${userParameters.plate_diameter} см `;
  });
  document.querySelector(
    ".weight-aim-value"
  ).textContent = `${userParameters.weight_aim} кг `;
  if (userParameters.weight_gap >= 0) {
    document.querySelector(".weight-gap-value").textContent = `(+${formatNumber(
      userParameters.weight_gap
    )} кг)`;
  } else {
    document.querySelector(".weight-gap-value").textContent = `(${formatNumber(
      userParameters.weight_gap
    )} кг)`;
  }
}

async function setUserStreak() {
  const userStreak = await sendData("/api/get_current_streak");
  document.querySelector(
    ".strick__time"
  ).textContent = `${userStreak.current_streak_text}`;
  const userStreakTaskText = userStreak.task_text.replace(/\n/g, "<br>");
  // document.querySelector(
  //   ".notion__p-motivation"
  // ).textContent = `${userStreak.task_text}`;
  document.querySelector(".notion__p-motivation").innerHTML =
    userStreakTaskText;
  document.querySelector(
    ".notion__p-completed"
  ).textContent = `${userStreak.tomorrow_text}`;
  document.querySelector(
    ".strick-coins"
  ).textContent = `${userStreak.coin_reward}`;

  const maxTasks = 3;
  const currentTaskNumber = userStreak.current_task_number;
  for (let i = 1; i <= maxTasks; i++) {
    const barElement = document.querySelector(`.strick-progress__bar${i}`);
    if (i <= currentTaskNumber) {
      barElement.classList.add("strick-progress__bar_green");
    }
  }
  if (currentTaskNumber === 1) {
    document.querySelector(
      ".stick-progress__lines__inner_middle"
    ).style.opacity = "0";
    document.querySelector(
      ".stick-progress__lines__inner_right"
    ).style.opacity = "0";
  } else if (currentTaskNumber === 2) {
    document.querySelector(".stick-progress__lines__inner_left").style.opacity =
      "0";
    document.querySelector(
      ".stick-progress__lines__inner_right"
    ).style.opacity = "0";
  } else {
    document.querySelector(".stick-progress__lines__inner_left").style.opacity =
      "0";
    document.querySelector(
      ".stick-progress__lines__inner_middle"
    ).style.opacity = "0";
  }
}

async function setNutrientParameters() {
  nutrientStreak = await sendData("/api/get_nutrient_parameters");
  const width = nutrientStreak.eaten_calories / nutrientStreak.day_calories;
  if (width > 1) {
    document.querySelector(".progress__foreground").style.width = "100%";
    document.querySelector(".progress__foreground").style.borderTopRightRadius =
      "3px";
    document.querySelector(
      ".progress__foreground"
    ).style.borderBottomRightRadius = "3px";
    document.querySelector(".progress__foreground").style.backgroundColor =
      "#ff0831";
  } else {
    document.querySelector(".progress__foreground").style.width = `${
      width * 80
    }%`;
  }
  document.querySelector(".day_calories").textContent = `100%`;
  document.querySelector(".eaten-calories").textContent = `${Math.floor(
    (nutrientStreak.eaten_calories * 100) / nutrientStreak.day_calories
  )}`;

  document.querySelector(".eaten__proteins").textContent = `${Math.floor(
    (nutrientStreak.eaten_proteins * 100) / nutrientStreak.day_proteins
  )}`;

  document.querySelector(".eaten__fats").textContent = `${Math.floor(
    (nutrientStreak.eaten_fats * 100) / nutrientStreak.day_fats
  )}`;

  document.querySelector(".eaten__carbohydrates").textContent = `${Math.floor(
    (nutrientStreak.eaten_carbohydrates * 100) /
      nutrientStreak.day_carbohydrates
  )}`;
}

async function setPlates() {
  const plates = await sendData("/api/get_today_plates");
  if (plates.length === 0) {
    document
      .querySelector(".eat__buttons-single")
      .classList.remove("eat__buttons-single_hidden");
  } else {
    document
      .querySelector(".eat__buttons-single")
      .classList.remove("eat__buttons-single_hidden");
    document.querySelector(".eat__buttons-single").textContent =
      "Изменить рацион";
    plates.forEach((plate, index) => {
      document.querySelector(".cards").insertAdjacentHTML(
        "beforeend",
        `<div class="card card${index + 1}" name="${plate.plate_id}">
    <div class="card__type">${plate.plate_type}</div>
    <div style="display: none" class="card__calories">Б: ${
      plate.proteins
    } / Ж: ${plate.fats} / У: ${plate.carbohydrates} / ${
          plate.calories
        } ккал</div>
    <div class="card__meal">“${plate.plate_name}”</div>
    <div class="card__visual card__visual${index + 1}">
      <div class="card__plate_frames"></div>
      <div class="card__plate_size">
        <div class="plate__arrow">
          <img src="../static/images/plate-arrow.svg" alt="" />
        </div>
        <div class="plate__size-title plate-diameter-value">
          ${diameter} см
        </div>
      </div>
    </div>
    <p class="card__list-description">Список блюд</p>
    <div class="card__list card__list${index + 1}">
    </div>
    <p class="card__difficulty card__difficulty${index + 1}">Сложность</p>
    <div class="card__stars card__stars${index + 1}">
    </div>
    <p class="total-time">Общее время приготовления</p>
    <p class="total-time_value">${plate.recipe_time} минут</p>
    <p class="active-time">Время "у плиты"</p>
    <p class="active-time_value">${plate.recipe_active_time} минут</p>
    <div class="card__buttons">
      <button class="card__button__recepi card__button__recepi${
        index + 1
      }">Рецепт</button>
      <button class="card__button__favourites card__button__favourites${
        index + 1
      }">Добавить в избранное</button>
      <button class="card__button__choose card__button__choose${
        index + 1
      }">${genderTextEaten}</button>
    </div>
  </div>`
      );

      plate.meals.forEach((el, i) => {
        document
          .querySelector(`.card__list${index + 1}`)
          .insertAdjacentHTML(
            "beforeend",
            `<p class="card__list__item">${i + 1}. ${el}</p>`
          );
      });

      if (plate.is_eaten === true) {
        document.querySelector(
          `.card__button__choose${index + 1}`
        ).textContent = genderTextNotEaten;
        document
          .querySelector(`.card__button__choose${index + 1}`)
          .classList.add("card__button__choose_off");
      }

      document
        .querySelector(`.card__button__recepi${index + 1}`)
        .addEventListener("click", (event) => {
          const data = {};
          data.plate_id = plate.plate_id;
          data.tg_id = tg_id;
          setRecepi(data);
          showRecepi();
        });

      document
        .querySelector(`.card__button__choose${index + 1}`)
        .addEventListener("click", (event) => {
          const data = {};
          data.plate_id = plate.plate_id;
          data.tg_id = tg_id;
          data.calories = plate.calories;
          data.proteins = plate.proteins;
          data.fats = plate.fats;
          data.carbohydrates = plate.carbohydrates;
          data.plate_type = plate.plate_type;
          sendPlate(data, "/api/has_eaten_plate", event.target);
        });

      if (plate.in_favorites === true) {
        document.querySelector(
          `.card__button__favourites${index + 1}`
        ).textContent = "Удалить из избранного";
        document
          .querySelector(`.card__button__favourites${index + 1}`)
          .classList.add("card__button__favourites_off");
      }

      document
        .querySelector(`.card__button__favourites${index + 1}`)
        .addEventListener("click", (event) => {
          const data = {};
          data.plate_id = plate.plate_id;
          data.tg_id = tg_id;
          sendFavoritePlate(data, "/api/add_to_favorites", event.target);
        });

      promises.push(setPlateImage("card__visual", plate, index));
      setPlateStars("card__stars", plate, index);
    });
  }
}

let isFunctionsLoaded = false;
let isImagesLoaded = false;

function handleCompletion(message) {
  isFunctionsLoaded = true;
  if (isImagesLoaded) {
    hideLoading();
  }
}

Promise.all([
  setUserParameters(),
  setUserStreak(),
  setNutrientParameters(),
  setPlates(),
])
  .catch((error) => {
    console.error("Произошла ошибка при выполнении функций:", error);
  })
  .finally(() => {
    Promise.all(promises)
      .then(() => handleCompletion("Все изображения загружены!"))
      .catch(() =>
        handleCompletion(
          "Ошибка при загрузке одного или нескольких изображений."
        )
      );
  });

function showLoading(param = true) {
  const loader = document.querySelector(".loading");
  loader.classList.remove("loading_hidden");
  loader.style.display = "flex";
  if (param) {
    document.body.style.overflow = "hidden";
  }
}

function hideLoading(param = true) {
  const loader = document.querySelector(".loading");
  loader.classList.add("loading_hidden");
  loader.addEventListener("transitionend", function () {
    loader.style.display = "none";
  });
  if (param) {
    document.body.style.overflow = "visible";
  }
}

window.onload = () => {
  isImagesLoaded = true;
  if (isFunctionsLoaded) {
    hideLoading();
  }
};

async function sendFavoritePlate(data, link, el) {
  try {
    showLoading();
    const request = await fetch(`..${link}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });
    const response = await request.json();
    hideLoading();
    if (response.success === true) {
      const cards = document.querySelectorAll(".card");
      cards.forEach((card) => {
        if (String(data.plate_id) === String(card.getAttribute("name"))) {
          const buttonText = !response.is_black
            ? "Удалить из избранного"
            : "Добавить в избранное";
          card.querySelector(".card__button__favourites").textContent =
            buttonText;
          card
            .querySelector(".card__button__favourites")
            .classList.toggle(
              "card__button__favourites_off",
              !response.is_black
            );
        }
      });
    }
  } catch (err) {
    console.log(err);
  }
}

let mark = 0;

async function sendPlate(data, link, el) {
  try {
    showLoading();
    const request = await fetch(`..${link}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });
    const response = await request.json();
    hideLoading();
    if (response.success === true) {
      if (response.is_green === false) {
        feedbackData = Object.assign({}, data);
        let starIndex = 1;
        const stars = document.querySelectorAll(".star");
        stars.forEach((star) => star.classList.remove("active"));
        stars.forEach((star) => {
          star.addEventListener("click", (event) => {
            const clickedStar = event.currentTarget;
            starIndex = clickedStar.getAttribute("data-index");
            mark = starIndex;

            stars.forEach((star) => star.classList.remove("active"));
            for (let i = 1; i <= starIndex; i++) {
              stars[i - 1].classList.add("active");
            }
          });
        });
        document
          .querySelector(".popup-feedback")
          .classList.remove("popup_hidden");
        document.querySelector(".error").classList.remove("error_active");
        const exit = document
          .querySelector(".popup-feedback")
          .querySelector(".exit");
        exit.addEventListener("click", (event) => {
          event.target.closest(".popup-feedback").classList.add("popup_hidden");
          if (
            document
              .querySelector(".popup-win")
              .classList.contains("popup_hidden")
          ) {
            document.body.style.overflow = "visible";
          }
        });

        document.body.style.overflow = "hidden";
      }

      if (response.completed_all_tasks === true) {
        document.querySelector(".bold-popup-title").textContent =
          response.bold_text;
        document.querySelector(".thin-popup-title").textContent =
          response.thin_text;
        document.querySelector(".popup-win").classList.remove("popup_hidden");
        document.body.style.overflow = "hidden";
        const exit = document
          .querySelector(".popup-win")
          .querySelector(".exit");
        exit.addEventListener("click", (event) => {
          event.target.closest(".popup-win").classList.add("popup_hidden");
          document.body.style.overflow = "visible";
        });

        const excellentButton = document.querySelector(".excellent-button");
        if (excellentButton)
          excellentButton.addEventListener("click", (event) => {
            event.target.closest(".popup-win").classList.add("popup_hidden");
            document.body.style.overflow = "visible";
          });
      }

      const eatenCaloriesEl = document.querySelector(".eaten-calories");
      const eatenProteinsEl = document.querySelector(".eaten__proteins");
      const eatenFatsEl = document.querySelector(".eaten__fats");
      const eatenCarbohydratesEl = document.querySelector(
        ".eaten__carbohydrates"
      );
      const progressForeground = document.querySelector(
        ".progress__foreground"
      );

      el.textContent = response.is_green ? genderTextEaten : genderTextNotEaten;
      el.classList.toggle("card__button__choose_off", !response.is_green);

      eatenCaloriesEl.textContent =
        +eatenCaloriesEl.textContent +
        (response.is_green
          ? Math.ceil((-data.calories * 100) / nutrientStreak.day_calories)
          : Math.floor((data.calories * 100) / nutrientStreak.day_calories));
      eatenProteinsEl.textContent =
        +eatenProteinsEl.textContent +
        (response.is_green
          ? Math.ceil((-data.proteins * 100) / nutrientStreak.day_proteins)
          : Math.floor((data.proteins * 100) / nutrientStreak.day_proteins));
      eatenFatsEl.textContent =
        +eatenFatsEl.textContent +
        (response.is_green
          ? Math.ceil((-data.fats * 100) / nutrientStreak.day_fats)
          : Math.floor((data.fats * 100) / nutrientStreak.day_fats));
      eatenCarbohydratesEl.textContent =
        +eatenCarbohydratesEl.textContent +
        (response.is_green
          ? Math.ceil(
              (-data.carbohydrates * 100) / nutrientStreak.day_carbohydrates
            )
          : Math.floor(
              (data.carbohydrates * 100) / nutrientStreak.day_carbohydrates
            ));
      const width = +eatenCaloriesEl.textContent;
      const progressBarStyle = progressForeground.style;
      progressBarStyle.width = width > 100 ? "100%" : `${width * 0.8}%`;
      progressBarStyle.borderTopRightRadius =
        progressBarStyle.borderBottomRightRadius = width > 100 ? "3px" : "0px";
      progressBarStyle.backgroundColor = width > 100 ? "#ff0831" : "#05ff00";
    }
  } catch (err) {
    console.log(err);
  }
}

function showRecepi() {
  document.querySelector(".popup-recepi").classList.remove("popup_hidden");
  document.body.style.overflow = "hidden";
}

async function sendMark(data, mark) {
  const obj = {};
  obj.tg_id = data.tg_id;
  obj.plate_id = data.plate_id;
  obj.mark = mark;
  showLoading(false);
  const request = await fetch(`../api/submit_plate_review`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(obj),
  });
  const response = await request.json();
  hideLoading(false);
}

async function setRecepi(data) {
  showLoading(false);
  document.querySelector(".popup__inner").innerHTML = "";
  document.querySelector(".popup__inner").insertAdjacentHTML(
    "afterbegin",
    ` <p class="popup__plate-title">
  “Название блюда длинasdf adsf asdf asd fasd fasdfasd”
</p>
<div class="exit">
  <img src="../static/images/exit.svg" alt="exit" />
</div>`
  );

  const request = await fetch(`../api/get_recipe`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });
  const response = await request.json();

  hideLoading(false);

  document.querySelector(
    ".popup__plate-title"
  ).textContent = `“${response.plate_name}”`;

  response.meals.forEach((meal, index) => {
    document.querySelector(".popup__inner").insertAdjacentHTML(
      "beforeend",
      `<div class="popup__meal popup__meal${index + 1}">
    <p class="popup__meal-title popup__meal-title${index + 1}">${index + 1}. ${
        meal.meal_name
      }</p>
    <p class="popup__ingredients">Ингредиенты:</p>
    <div class="popup__ingredients-flex popup__ingredients-flex${index + 1}">
    </div>
    <p class="popup__recepi">Рецепт:</p>
    <p class="popup__recepi__text">
      ${meal.recipe}
    </p>
    <div class="popup__time">
      <div class="popup__time-flex">
        <p class="popup__time-current">Время "у плиты" (минут)</p>
        <p class="popup__time-current__value">${meal.recipe_active_time}</p>
      </div>
      <div class="popup__time-flex">
        <p class="popup__time-total">Общее время (минут)</p>
        <p class="popup__time-total__value">${meal.recipe_time}</p>
      </div>
    </div>
    <hr class="hr hr-20" />
  </div>`
    );

    meal.ingredients.forEach((ingredient, i) => {
      document
        .querySelector(`.popup__ingredients-flex${index + 1}`)
        .insertAdjacentHTML(
          "beforeend",
          ` <div class="popup__ingredients${i + 1}">
        <p class="popup__ingredients__title"><span class="number-indicator">${
          i + 1
        }.</span> ${ingredient.ingredient_name}</p>
        <p class="popup__ingredients__amount">количество: ${
          ingredient.ingredient_amount
        }</p>
        <p class="popup__ingredients__measure">мера: ${
          ingredient.ingredient_measure
        }</p>
      </div>`
        );
    });
  });
  const exit = document.querySelector(".popup-recepi").querySelector(".exit");
  exit.addEventListener("click", (event) => {
    event.target.closest(".popup-recepi").classList.add("popup_hidden");
    document.body.style.overflow = "visible";
  });
}

const excellentButton = document
  .querySelector(".popup-feedback")
  .querySelector(".excellent-button");
if (excellentButton)
  excellentButton.addEventListener("click", (event) => {
    if (mark <= 0) {
      document.querySelector(".error").classList.add("error_active");
    } else {
      event.target.closest(".popup-feedback").classList.add("popup_hidden");
      if (
        document.querySelector(".popup-win").classList.contains("popup_hidden")
      ) {
        document.body.style.overflow = "visible";
      }
      document.querySelector(".error").classList.remove("error_active");
      sendMark(feedbackData, mark);
      mark = 0;
    }
  });

async function handleButtonClick(endpoint) {
  try {
    showLoading(false);
    const response = await fetch(endpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ tg_id: tg_id }),
    });

    const data = await response.json();
    if (data.success === true) {
      tg.close();
    } else {
      tg.close();
    }
  } catch (err) {
    console.log(err);
  } finally {
    tg.close();
    hideLoading(false);
  }
}

document.querySelector(".i_have_eaten").addEventListener("click", function () {
  handleButtonClick("../api/get_has_eaten_without_plates_post");
});
document
  .querySelector(".what_can_i_eat")
  .addEventListener("click", function () {
    handleButtonClick("../api/what_else_to_eat_post");
  });
document
  .querySelector(".button_ask-question")
  .addEventListener("click", function () {
    handleButtonClick("../api/ask_question");
  });
