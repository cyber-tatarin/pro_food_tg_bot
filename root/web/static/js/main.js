let choicesCounter = 1;

const renderSelect = () => {
  const elements = document.querySelectorAll(`.js-choice_${choicesCounter++}`);
  elements.forEach((el) => {
    const choices = new Choices(el, {
      itemSelectText: "",
      noResultsText: "Не найдено",
    });
    el.addEventListener(
      "choice",
      function (event) {
        document
          .querySelectorAll(".choices__inner")
          .forEach((el) => (el.style.color = "#303030"));
      },
      false
    );
  });
};

renderSelect();

const button = document.querySelector(".dish__add");
button.addEventListener("click", (event) => {
  event.preventDefault();
  button.insertAdjacentHTML(
    "beforebegin",
    `<div class="dish__item dish__item_new">
<p class="dish__title">Ингридиент 1 (в мере "ладонь")</p>
<select class="js-choice_${choicesCounter}">
  <option value="" selected>Введите ингридиент</option>
  <option value="1">Кафе</option>
  <option value="2">Финтес клуб</option>
  <option value="3">Пиццерия</option>
  <option value="4">Реклама</option>
  <option value="5">Салон красоты</option>
  <option value="6">Шаурмичная</option>
  <option value="7">Бургерная</option>
  <option value="8">Кальянная</option>
  <option value="9">Суши-бар</option>
  <option value="10">Интернет-магазин</option>
  <option value="11">Рыбалка</option>
  <option value="12">Пчеловодство</option>
  <option value="13">Медицина</option>
  <option value="14">Маркетинг</option>
</select>
<p class="dish__title">Количество</p>
<input
  class="input input_grey"
  type="number"
  maxlength="100"
  placeholder="Введите количество на 1 порцию"
  required
/>
<div class="dish__amount">450 / 10 / 20 / 4</div>
</div>`
  );
  console.log(choicesCounter);

  const elements = document.querySelectorAll(`.js-choice_${choicesCounter++}`);
  elements.forEach((el) => {
    const choices = new Choices(el, {
      itemSelectText: "",
      noResultsText: "Не найдено",
    });
    el.addEventListener(
      "choice",
      function (event) {
        el.parentElement.style.color = "#303030";
      },
      false
    );
  });
});
