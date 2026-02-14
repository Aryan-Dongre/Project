document.addEventListener('DOMContentLoaded', function () {

 
  // SERVICE TYPE PIE CHART
 

  const serviceTypeChart = document.getElementById('serviceTypeChart');

  if (serviceTypeChart) {
    fetch('/admin/services/analytics/service-type')
      .then(response => {
        if (!response.ok) {
          throw new Error('Failed to fetch service type analytics');
        }
        return response.json();
      })
      .then(data => {
        console.log('Service Type Analytics Data:', data);

        new Chart(serviceTypeChart, {
          type: 'pie', // graph type
          data: {
            labels: Object.keys(data),
            datasets: [{
              data: Object.values(data)
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false
          }
        });
      })
      .catch(error => {
        console.error('Service Type Analytics Error:', error);
      });
  }

 
  // SERVICE STATUS PIE CHART
 

  const serviceStatusChart = document.getElementById('serviceStatusChart');

  if (serviceStatusChart) {
    fetch('/admin/services/analytics/status')
      .then(response => {
        if (!response.ok) {
          throw new Error('Failed to fetch service status analytics');
        }
        return response.json();
      })
      .then(data => {
        console.log('Service Status Analytics Data:', data);

        new Chart(serviceStatusChart, {
          type: 'doughnut', // graph type
          data: {
            labels: Object.keys(data),  //Active, inactive
            datasets: [{
              data: Object.values(data) // active inactive counts
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false
          }
        });
      })
      .catch(error => {
        console.error('Service Status Analytics Error:', error);
      });
  }

   // MOST BOOKED SERVICES - BAR CHART

  const mostBookedChart = document.getElementById('mostBookedServiceChart');

if (mostBookedChart) {
  fetch('/admin/services/analytics/most-booked')
    .then(response => {
      if (!response.ok) {
        throw new Error('Failed to fetch most booked services');
      }
      return response.json();
    })
    .then(data => {
      console.log('Most Booked Services Data:', data);

     new Chart(mostBookedChart, {
  type: 'bar',
  data: {
    labels: data.labels,
    datasets: [{
      data: data.values,
      borderRadius: 8,
      barPercentage: 0.75,
      categoryPercentage: 0.8
    }]
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      x: {
        grid: { display: false },
        ticks: {
          maxRotation: 0,
          minRotation: 0,
          callback: function (value) {
            const label = this.getLabelForValue(value);
            return label.length > 16
              ? label.substring(0, 16) + '…'
              : label;
          },
          font: { size: 13 }
        }
      },
      y: {
        beginAtZero: true,
        grid: {
          color: 'rgba(0,0,0,0.05)'
        },
        ticks: {
          stepSize: 2,
          font: { size: 13 }
        }
      }
    },
    plugins: {
      legend: { display: false },
      tooltip: {
        callbacks: {
          label: ctx => ` Bookings: ${ctx.parsed.y}`
        }
      }
    }
  }
});

    })
    .catch(error => {
      console.error('Most Booked Services Analytics Error:', error);
    });
}





























});
