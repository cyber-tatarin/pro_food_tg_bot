const tg = window.Telegram.WebApp;
const tg_id = 459471362 || tg.initDataUnsafe.user.id;

let isFunctionsLoaded = true;
let isImagesLoaded = false;

function showLoading(param = true) {
  const loader = document.querySelector(".loading");
  loader.classList.remove("loading_hidden");
  loader.style.display = "flex";
  if (param) {
    console.log("hidden");
    document.body.style.overflow = "hidden";
  }
}

async function setStatistics() {
  try {
    const request = await fetch(`/api/statistics`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ tg_id: tg_id }),
    });
    const response = await request.json();
    if (!isEmpty(response)) {
      registerChart("weightChart", response.weight_list, "кг");
      registerChart("chestVolumeChart", response.chest_volume_list, "см");
      registerChart(
        "underchestVolumeChart",
        response.underchest_volume_list,
        "см"
      );
      registerChart("hipsVolumeChart", response.waist_volume_list, "см");
      registerChart("bellyVolumeChart", response.belly_volume_list, "см");
      registerChart("waistVolumeChart", response.hips_volume_list, "см");
      // hideLoading();
    } else {
      document
        .querySelector(".empty-list")
        .classList.remove("empty-list_hidden");
      document.querySelector(".graphic-flex").style.display = "none";
      console.log("Пустой JSON");
    }
  } catch (err) {
    console.log(err);
  }
}

function isEmpty(obj) {
  if (Object.keys(obj).length === 0) return true;

  for (let key in obj) {
    if (obj[key] !== null && obj[key] !== undefined && obj[key].length !== 0)
      return false;
  }

  return true;
}

setStatistics();

function hideLoading(param = true) {
  const loader = document.querySelector(".loading");
  loader.classList.add("loading_hidden");
  loader.addEventListener("transitionend", function () {
    loader.style.display = "none";
  });
  if (param) {
    console.log("visible");
    document.body.style.overflow = "visible";
  }
}

window.onload = () => {
  console.log("successfully");
  isImagesLoaded = true;
  if (isFunctionsLoaded) {
    hideLoading();
  }
};

const skipped = (ctx, value) =>
  ctx.p0.skip || ctx.p1.skip ? value : undefined;
const down = (ctx, value) =>
  ctx.p0.parsed.y > ctx.p1.parsed.y ? value : undefined;

const chartAreaBorder = {
  id: "chartAreaBorder",
  beforeDraw(chart, args, options) {
    const {
      ctx,
      chartArea: { left, top, width, height },
    } = chart;
    ctx.save();
    ctx.strokeStyle = options.borderColor;
    ctx.lineWidth = options.borderWidth;
    ctx.setLineDash(options.borderDash || []);
    ctx.lineDashOffset = options.borderDashOffset;

    ctx.beginPath();
    ctx.moveTo(left, top);
    ctx.lineTo(left, top + height);
    ctx.stroke();

    ctx.beginPath();
    ctx.moveTo(left, top + height);
    ctx.lineTo(left + width, top + height);
    ctx.stroke();

    ctx.restore();
  },
};

function createConfig(dates, values, min, max, measure) {
  return {
    type: "line",
    data: {
      labels: dates,
      datasets: [
        {
          label: null,
          data: values,
          segment: {
            borderColor: (ctx) =>
              skipped(ctx, "rgb(0,0,0,0.2)") || down(ctx, "#05ff00") || "#f00",
            borderDash: (ctx) => skipped(ctx, [6, 6]),
          },
          spanGaps: true,
          pointRadius: 0,
          pointHitRadius: 10,
        },
      ],
    },
    options: {
      plugins: {
        legend: { display: false },
        chartAreaBorder: {
          borderColor: "#303030",
          borderWidth: 2,
        },
        tooltip: {
          mode: "index",
          displayColors: false,
          backgroundColor: "rgba(0,0,0,0.5)",
          titleFont: { family: "Montserrat", size: 16 },
          bodyFont: { family: "Montserrat", size: 14 },
          callbacks: {
            title: function (context) {
              return context[0].label;
            },
            label: function (context) {
              return context.parsed.y + ` ${measure}`;
            },
          },
        },
      },
      scales: {
        y: {
          min: min - 1,
          max: max + 1,
          ticks: {
            stepSize: 1,
            color: "#303030",
          },
          grid: { display: false },
        },
        x: {
          offset: true, // Добавляет отступ к концам шкалы
          // max: 100,
          ticks: {
            display: true,
            color: "#303030",
          },
          grid: { display: false },
        },
      },
    },
    plugins: [chartAreaBorder],
  };
}

function registerChart(element, list, measure) {
  const dates = [];
  const values = [];
  const allValues = [];

  list.forEach((el) => {
    dates.push(el.date);
    allValues.push(el.value);
    if (el.value !== null) {
      values.push(el.value); // сохраняем только ненулевые значения
    }
  });

  const minValue = Math.min(...values);
  const maxValue = Math.max(...values);
  document.querySelector(`.${element}-min-value`).textContent = minValue;
  document.querySelector(`.${element}-max-value`).textContent = maxValue;
  const ctx = document.getElementById(element).getContext("2d");
  const myChart = new Chart(
    ctx,
    createConfig(dates, allValues, minValue, maxValue, measure)
  );
  Chart.defaults.font.family = "Montserrat";
  Chart.defaults.font.weight = "normal"; // или 'bold', 'light', и т.д.

  // Chart.register(horizontalLinePlugin);
}

const test = {
  weight_list: [
    { date: "02.01.2023", value: 60 },
    // { date: "03.01.2023", value: 50 },
    // { date: "05.01.2023", value: 70 },
    // { date: "02.01.2023", value: 60 },
    // { date: "03.01.2023", value: 50 },
    // { date: "05.01.2023", value: 70 },
    // { date: "02.01.2023", value: 60 },
    // { date: "03.01.2023", value: 50 },
    // { date: "05.01.2023", value: 70 },
    // { date: "02.01.2023", value: 60 },
    // { date: "03.01.2023", value: 50 },
    // { date: "05.01.2023", value: 70 },
    // { date: "02.01.2023", value: 60 },
    // { date: "03.01.2023", value: 50 },
    // { date: "05.01.2023", value: 70 },
    // { date: "05.01.2023", value: 70 },
    // { date: "05.01.2023", value: 70 },
    // { date: "05.01.2023", value: 70 },
    // { date: "05.01.2023", value: 70 },
    // { date: "05.01.2023", value: 70 },
    // { date: "05.01.2023", value: 70 },
    // { date: "05.01.2023", value: 70 },
    // { date: "05.01.2023", value: 70 },
    // { date: "05.01.2023", value: 70 },
    // { date: "05.01.2023", value: 70 },
    // { date: "05.01.2023", value: 70 },
  ],
  chest_volume_list: [
    { date: "02.01.2023", value: 60 },
    { date: "03.01.2023", value: 50 },
    { date: "05.01.2023", value: 70 },
  ],
  underchest_volume_list: [
    { date: "02.01.2023", value: 60 },
    { date: "03.01.2023", value: 50 },
    { date: "05.01.2023", value: 70 },
  ],
  waist_volume_list: [
    { date: "02.01.2023", value: 60 },
    { date: "03.01.2023", value: 50 },
    { date: "05.01.2023", value: 70 },
  ],
  belly_volume_list: [
    { date: "02.01.2023", value: 60 },
    { date: "03.01.2023", value: 50 },
    { date: "05.01.2023", value: 70 },
  ],
  hips_volume_list: [
    { date: "02.01.2023", value: 60 },
    { date: "03.01.2023", value: 50 },
    { date: "05.01.2023", value: 70 },
  ],
};

// registerChart("weightChart", test.weight_list, "кг");
// registerChart("chestVolumeChart", test.chest_volume_list, "см");
// registerChart("underchestVolumeChart", test.underchest_volume_list, "см");
// registerChart("hipsVolumeChart", test.waist_volume_list, "см");
// registerChart("bellyVolumeChart", test.belly_volume_list, "см");
// registerChart("waistVolumeChart", test.hips_volume_list, "см");
