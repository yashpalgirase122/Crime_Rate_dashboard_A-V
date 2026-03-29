document.addEventListener('DOMContentLoaded', async () => {
    try {
        const response = await fetch('/api/crime_data');
        const data = await response.json();
        if(Object.keys(data).length === 0) return;

        const colors = [
            'rgba(59, 130, 246, 0.8)',
            'rgba(16, 185, 129, 0.8)',
            'rgba(245, 158, 11, 0.8)',
            'rgba(239, 68, 68, 0.8)',
            'rgba(139, 92, 246, 0.8)'
        ];

        // 1. Bar Chart -> Crime by city
        const cityCtx = document.getElementById('cityChart');
        if (cityCtx) {
            new Chart(cityCtx.getContext('2d'), {
                type: 'bar',
                data: {
                    labels: Object.keys(data.city_distribution),
                    datasets: [{
                        label: 'Crimes by City',
                        data: Object.values(data.city_distribution),
                        backgroundColor: colors
                    }]
                },
                options: { responsive: true, plugins: { legend: { display: false } } }
            });
        }

        // 2. Pie Chart -> Crime categories
        const catCtx = document.getElementById('categoryChart');
        if (catCtx) {
            new Chart(catCtx.getContext('2d'), {
                type: 'pie',
                data: {
                    labels: Object.keys(data.category_distribution),
                    datasets: [{
                        data: Object.values(data.category_distribution),
                        backgroundColor: colors,
                        borderWidth: 0
                    }]
                },
                options: { responsive: true }
            });
        }

        // 3. Line Chart -> Yearly trend
        const lineCtx = document.getElementById('trendChart');
        if (lineCtx) {
            new Chart(lineCtx.getContext('2d'), {
                type: 'line',
                data: {
                    labels: Object.keys(data.yearly_trend),
                    datasets: [{
                        label: 'Yearly Crime Trend',
                        data: Object.values(data.yearly_trend),
                        borderColor: 'rgba(59, 130, 246, 1)',
                        borderWidth: 2,
                        fill: false,
                        tension: 0.4
                    }]
                },
                options: { responsive: true }
            });
        }

        // 4. Area Chart -> Future Predictions (We pull this from the global variable rendered by jinja)
        const areaCtx = document.getElementById('forecastChart');
        if (areaCtx && window.forecastData) {
            new Chart(areaCtx.getContext('2d'), {
                type: 'line', // Area chart in Chart.js is line with fill option
                data: {
                    labels: Object.keys(window.forecastData),
                    datasets: [{
                        label: 'Predicted Crime Forecast',
                        data: Object.values(window.forecastData),
                        borderColor: 'rgba(16, 185, 129, 1)',
                        backgroundColor: 'rgba(16, 185, 129, 0.2)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: { responsive: true }
            });
        }

    } catch (e) {
        console.error('Error loading chart data', e);
    }
});
