/**
 * Enhanced Charts Module - Advanced charting with perfice-inspired features
 */

const EnhancedCharts = {
    // Store chart instances
    charts: {},

    // Initialize weekly chart with enhanced features
    initWeeklyChart(canvasId, viewType = 'daily') {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return;

        // Destroy existing chart if it exists
        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
        }

        // Get data based on view type
        let labels, data;
        switch (viewType) {
            case 'weekly':
                labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
                data = [65, 59, 80, 81, 56, 55, 40]; // Placeholder data
                break;
            case 'monthly':
                labels = ['Week 1', 'Week 2', 'Week 3', 'Week 4'];
                data = [180, 200, 190, 210]; // Placeholder data
                break;
            case 'daily':
            default:
                labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
                data = [65, 59, 80, 81, 56, 55, 40]; // Placeholder data
                break;
        }

        const config = {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Overall Progress',
                    data: data,
                    fill: true,
                    borderColor: '#6366f1',
                    backgroundColor: 'rgba(99, 102, 241, 0.1)',
                    tension: 0.4,
                    pointRadius: 4,
                    pointBackgroundColor: '#fff',
                    pointBorderWidth: 2,
                    pointHoverRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: 'rgba(30, 41, 59, 0.9)',
                        titleColor: '#f1f5f9',
                        bodyColor: '#cbd5e1',
                        borderColor: '#475569',
                        borderWidth: 1,
                        padding: 12,
                        displayColors: false,
                        callbacks: {
                            label: function(context) {
                                return `${context.dataset.label}: ${context.parsed.y}%`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        grid: {
                            color: 'rgba(226, 232, 240, 0.1)'
                        },
                        ticks: {
                            color: 'rgba(148, 163, 184, 0.8)',
                            callback: function(value) {
                                return value + '%';
                            }
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            color: 'rgba(148, 163, 184, 0.8)'
                        }
                    }
                },
                interaction: {
                    intersect: false,
                    mode: 'index'
                },
                animation: {
                    duration: 1000,
                    easing: 'easeOutQuart'
                }
            }
        };

        this.charts[canvasId] = new Chart(canvas, config);
    },

    // Initialize goal progress chart
    initGoalProgressChart(canvasId, goalData) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return;

        // Destroy existing chart if it exists
        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
        }

        // Prepare data for the chart
        const labels = goalData.labels || ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'];
        const progressData = goalData.progress || [20, 35, 50, 65, 80, 90];
        const targetData = goalData.target || [25, 40, 55, 70, 85, 100];

        const config = {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Actual Progress',
                        data: progressData,
                        fill: false,
                        borderColor: '#10b981',
                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                        tension: 0.4,
                        pointRadius: 4,
                        pointBackgroundColor: '#fff',
                        pointBorderWidth: 2,
                        pointHoverRadius: 6
                    },
                    {
                        label: 'Target Progress',
                        data: targetData,
                        fill: false,
                        borderColor: '#6366f1',
                        borderDash: [5, 5],
                        tension: 0.4,
                        pointRadius: 0
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            color: 'rgba(30, 41, 59, 0.8)',
                            usePointStyle: true
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(30, 41, 59, 0.9)',
                        titleColor: '#f1f5f9',
                        bodyColor: '#cbd5e1',
                        borderColor: '#475569',
                        borderWidth: 1,
                        padding: 12
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        grid: {
                            color: 'rgba(226, 232, 240, 0.1)'
                        },
                        ticks: {
                            color: 'rgba(148, 163, 184, 0.8)',
                            callback: function(value) {
                                return value + '%';
                            }
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            color: 'rgba(148, 163, 184, 0.8)'
                        }
                    }
                },
                interaction: {
                    intersect: false,
                    mode: 'index'
                },
                animation: {
                    duration: 1000,
                    easing: 'easeOutQuart'
                }
            }
        };

        this.charts[canvasId] = new Chart(canvas, config);
    },

    // Initialize dual-axis chart for comparing two metrics
    initDualAxisChart(canvasId, data) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return;

        // Destroy existing chart if it exists
        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
        }

        const config = {
            type: 'line',
            data: {
                labels: data.labels || ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [
                    {
                        label: data.firstLabel || 'Metric 1',
                        data: data.first || [65, 59, 80, 81, 56, 55],
                        fill: true,
                        borderColor: '#6366f1',
                        backgroundColor: 'rgba(99, 102, 241, 0.1)',
                        tension: 0.4,
                        yAxisID: 'y',
                        pointRadius: 4,
                        pointBackgroundColor: '#fff',
                        pointBorderWidth: 2,
                        pointHoverRadius: 6
                    },
                    {
                        label: data.secondLabel || 'Metric 2',
                        data: data.second || [28, 48, 40, 19, 86, 27],
                        fill: true,
                        borderColor: '#ec4899',
                        backgroundColor: 'rgba(236, 72, 153, 0.1)',
                        tension: 0.4,
                        yAxisID: 'y1',
                        pointRadius: 4,
                        pointBackgroundColor: '#fff',
                        pointBorderWidth: 2,
                        pointHoverRadius: 6
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false
                },
                scales: {
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        grid: {
                            color: 'rgba(226, 232, 240, 0.1)'
                        },
                        ticks: {
                            color: 'rgba(148, 163, 184, 0.8)'
                        }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        grid: {
                            drawOnChartArea: false,
                        },
                        ticks: {
                            color: 'rgba(148, 163, 184, 0.8)'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            color: 'rgba(148, 163, 184, 0.8)'
                        }
                    }
                },
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            color: 'rgba(30, 41, 59, 0.8)',
                            usePointStyle: true
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(30, 41, 59, 0.9)',
                        titleColor: '#f1f5f9',
                        bodyColor: '#cbd5e1',
                        borderColor: '#475569',
                        borderWidth: 1,
                        padding: 12
                    }
                }
            }
        };

        this.charts[canvasId] = new Chart(canvas, config);
    },

    // Initialize pie chart for categorical data
    initPieChart(canvasId, data) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return;

        // Destroy existing chart if it exists
        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
        }

        const config = {
            type: 'pie',
            data: {
                labels: data.labels || ['Category A', 'Category B', 'Category C', 'Category D'],
                datasets: [{
                    data: data.values || [30, 25, 20, 25],
                    backgroundColor: [
                        '#6366f1',
                        '#ec4899',
                        '#10b981',
                        '#f59e0b'
                    ],
                    borderColor: [
                        '#4f46e5',
                        '#db2777',
                        '#059669',
                        '#d97706'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: 'rgba(30, 41, 59, 0.8)',
                            padding: 20,
                            usePointStyle: true
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(30, 41, 59, 0.9)',
                        titleColor: '#f1f5f9',
                        bodyColor: '#cbd5e1',
                        borderColor: '#475569',
                        borderWidth: 1,
                        padding: 12
                    }
                },
                animation: {
                    duration: 1000,
                    easing: 'easeOutQuart'
                }
            }
        };

        this.charts[canvasId] = new Chart(canvas, config);
    },

    // Update an existing chart with new data
    updateChart(canvasId, newData) {
        const chart = this.charts[canvasId];
        if (!chart) return;

        // Update the chart data
        chart.data.datasets[0].data = newData.data || chart.data.datasets[0].data;
        if (newData.labels) {
            chart.data.labels = newData.labels;
        }
        
        // Update additional datasets if provided
        if (newData.datasets) {
            for (let i = 0; i < newData.datasets.length; i++) {
                if (chart.data.datasets[i]) {
                    chart.data.datasets[i].data = newData.datasets[i].data || chart.data.datasets[i].data;
                    if (newData.datasets[i].label) {
                        chart.data.datasets[i].label = newData.datasets[i].label;
                    }
                } else {
                    chart.data.datasets.push(newData.datasets[i]);
                }
            }
        }

        chart.update();
    },

    // Destroy a chart instance
    destroyChart(canvasId) {
        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
            delete this.charts[canvasId];
        }
    },

    // Destroy all charts
    destroyAllCharts() {
        Object.keys(this.charts).forEach(id => {
            this.charts[id].destroy();
        });
        this.charts = {};
    }
};

// Export for use in other modules
window.EnhancedCharts = EnhancedCharts;