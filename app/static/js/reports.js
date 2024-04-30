/**
 * 
 * @param {CanvasRenderingContext2D} ctx 
 * @param {Array} data 
 */
function showRevenueChart (ctx, data,) {
  const series = [
    [],[],[]
  ]

  // Map the data to the series
  Object.keys(data).forEach((key) => {
    const row = data[key];
    series[0].push(Number(row['subscription']));
    series[1].push(Number(row['lesson']));
    series[2].push(Number(row['workshop']));
  });

  // Create a stacked bar chart
  const chartData = {
    type: 'bar',
    data: {
      labels: Object.keys(data),
      datasets: [
        {
          label: 'Subscription',
          data: series[0],
        },
        {
          label: 'Lesson',
          data: series[1],
        },
        {
          label: 'Workshop',
          data: series[2],
        }
      ],
    },
    options: {
      scales: {
        y: {
          beginAtZero: true,
          stacked: true,
        },
        x: {
          stacked: true,
        },
      },
    },
  };
  new Chart(ctx, chartData);
}

/**
 * Display the workshop chart
 * @param {CanvasRenderingContext2D} ctx 
 * @param {Array} data 
 */
function showWorkshopChart(ctx, data) {
  const series = [
    [], []
  ];

  const labels = [];
  // Map the data to the series and labels
  Object.keys(data).forEach((key) => {
    const row = data[key];
    labels.push(row['title']);
    series[0].push(Number(row['booking_count']));
    series[1].push(Number(row['attended_count']));
  });

  // Create a bar chart
  const chartData = {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [
        {
          label: 'Booked',
          data: series[0],
        },
        {
          label: 'Attended',
          data: series[1],
        },
      ],
    },
  };
  new Chart(ctx, chartData);
}

/**
 * Display the attendance chart
 * @param {CanvasRenderingContext2D} ctx 
 * @param {Array} data 
 */
function showAttendanceChart(ctx, data) {
  const series = [
    [], [], [], []
  ];

  const labels = [];
  // Map the data to the series and labels
  Object.keys(data).forEach((key) => {
    const row = data[key];
    labels.push(row['name']);
    series[0].push(Number(row['lesson_booked']));
    series[1].push(Number(row['lesson_attended']));
    series[2].push(Number(row['workshop_booked']));
    series[3].push(Number(row['workshop_attended']));
  });

  // Create a stacked bar chart
  const chartData = {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [
        {
          label: 'Lessons Booked',
          data: series[0],
          stack: 'stack 0',
        },
        {
          label: 'Lessons Attended',
          data: series[1],
          stack: 'stack 1',
        },
        {
          label: 'Workshops Booked',
          data: series[2],
          stack: 'stack 0',
        },
        {
          label: 'Workshops Attended',
          data: series[3],
          stack: 'stack 1',
        },
      ],
    },
  };
  new Chart(ctx, chartData);
}
