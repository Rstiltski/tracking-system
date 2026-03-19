import { useState, useEffect } from 'react'
import axios from 'axios'
import ApiHealthDashboard from './ApiHealthDashboard'

const API_BASE = '/api'

function App() {
    const [view, setView] = useState('dashboard')
    const [status, setStatus] = useState(null)

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Header */}
            <header className="bg-white shadow-sm">
                <div className="max-w-7xl mx-auto px-4 py-4">
                    <h1 className="text-2xl font-bold text-gray-900">
                        Veryfyn Tracking System
                    </h1>
                    <p className="text-sm text-gray-500">Decoupled Architecture - React Frontend</p>
                </div>
            </header>

            {/* Navigation */}
            <nav className="bg-white border-b">
                <div className="max-w-7xl mx-auto px-4">
                    <div className="flex space-x-8 overflow-x-auto">
                        <button
                            onClick={() => setView('dashboard')}
                            className={`py-4 px-1 border-b-2 font-medium text-sm whitespace-nowrap ${view === 'dashboard'
                                ? 'border-primary-500 text-primary-600'
                                : 'border-transparent text-gray-500 hover:text-gray-700'
                                }`}
                        >
                            Dashboard
                        </button>
                        <button
                            onClick={() => setView('habits')}
                            className={`py-4 px-1 border-b-2 font-medium text-sm whitespace-nowrap ${view === 'habits'
                                ? 'border-primary-500 text-primary-600'
                                : 'border-transparent text-gray-500 hover:text-gray-700'
                                }`}
                        >
                            Habits
                        </button>
                        <button
                            onClick={() => setView('tasks')}
                            className={`py-4 px-1 border-b-2 font-medium text-sm whitespace-nowrap ${view === 'tasks'
                                ? 'border-primary-500 text-primary-600'
                                : 'border-transparent text-gray-500 hover:text-gray-700'
                                }`}
                        >
                            Tasks
                        </button>
                        <button
                            onClick={() => setView('goals')}
                            className={`py-4 px-1 border-b-2 font-medium text-sm whitespace-nowrap ${view === 'goals'
                                ? 'border-primary-500 text-primary-600'
                                : 'border-transparent text-gray-500 hover:text-gray-700'
                                }`}
                        >
                            Goals
                        </button>
                        <button
                            onClick={() => setView('health')}
                            className={`py-4 px-1 border-b-2 font-medium text-sm whitespace-nowrap ${view === 'health'
                                ? 'border-primary-500 text-primary-600'
                                : 'border-transparent text-gray-500 hover:text-gray-700'
                                }`}
                        >
                            Health
                        </button>
                        <button
                            onClick={() => setView('time')}
                            className={`py-4 px-1 border-b-2 font-medium text-sm whitespace-nowrap ${view === 'time'
                                ? 'border-primary-500 text-primary-600'
                                : 'border-transparent text-gray-500 hover:text-gray-700'
                                }`}
                        >
                            Time
                        </button>
                        <button
                            onClick={() => setView('finances')}
                            className={`py-4 px-1 border-b-2 font-medium text-sm whitespace-nowrap ${view === 'finances'
                                ? 'border-primary-500 text-primary-600'
                                : 'border-transparent text-gray-500 hover:text-gray-700'
                                }`}
                        >
                            Finances
                        </button>
                        <button
                            onClick={() => setView('emotional')}
                            className={`py-4 px-1 border-b-2 font-medium text-sm whitespace-nowrap ${view === 'emotional'
                                ? 'border-primary-500 text-primary-600'
                                : 'border-transparent text-gray-500 hover:text-gray-700'
                                }`}
                        >
                            Emotional
                        </button>
                        <button
                            onClick={() => setView('achievements')}
                            className={`py-4 px-1 border-b-2 font-medium text-sm whitespace-nowrap ${view === 'achievements'
                                ? 'border-primary-500 text-primary-600'
                                : 'border-transparent text-gray-500 hover:text-gray-700'
                                }`}
                        >
                            Achievements
                        </button>
                        <button
                            onClick={() => setView('insights')}
                            className={`py-4 px-1 border-b-2 font-medium text-sm whitespace-nowrap ${view === 'insights'
                                ? 'border-primary-500 text-primary-600'
                                : 'border-transparent text-gray-500 hover:text-gray-700'
                                }`}
                        >
                            Insights
                        </button>
                        <button
                            onClick={() => setView('calendar')}
                            className={`py-4 px-1 border-b-2 font-medium text-sm whitespace-nowrap ${view === 'calendar'
                                ? 'border-primary-500 text-primary-600'
                                : 'border-transparent text-gray-500 hover:text-gray-700'
                                }`}
                        >
                            Calendar
                        </button>
                        <button
                            onClick={() => setView('reports')}
                            className={`py-4 px-1 border-b-2 font-medium text-sm whitespace-nowrap ${view === 'reports'
                                ? 'border-primary-500 text-primary-600'
                                : 'border-transparent text-gray-500 hover:text-gray-700'
                                }`}
                        >
                            Reports
                        </button>
                        <button
                            onClick={() => setView('settings')}
                            className={`py-4 px-1 border-b-2 font-medium text-sm whitespace-nowrap ${view === 'settings'
                                ? 'border-primary-500 text-primary-600'
                                : 'border-transparent text-gray-500 hover:text-gray-700'
                                }`}
                        >
                            Settings
                        </button>
                        <button
                            onClick={() => setView('test')}
                            className={`py-4 px-1 border-b-2 font-medium text-sm whitespace-nowrap ${view === 'test'
                                ? 'border-primary-500 text-primary-600'
                                : 'border-transparent text-gray-500 hover:text-gray-700'
                                }`}
                        >
                            API Test
                        </button>
                    </div>
                </div>
            </nav>

            {/* Main Content */}
            <main className="max-w-7xl mx-auto px-4 py-8">
                {status && (
                    <div className={`mb-4 p-4 rounded ${status.type === 'error' ? 'bg-red-50 text-red-800' : 'bg-green-50 text-green-800'
                        }`}>
                        {status.message}
                    </div>
                )}

                {view === 'dashboard' && <DashboardView setStatus={setStatus} />}
                {view === 'habits' && <HabitsView setStatus={setStatus} />}
                {view === 'tasks' && <TasksView setStatus={setStatus} />}
                {view === 'goals' && <GoalsView setStatus={setStatus} />}
                {view === 'health' && <HealthView setStatus={setStatus} />}
                {view === 'time' && <TimeView setStatus={setStatus} />}
                {view === 'finances' && <FinancesView setStatus={setStatus} />}
                {view === 'emotional' && <EmotionalHealthView setStatus={setStatus} />}
                {view === 'achievements' && <AchievementsView setStatus={setStatus} />}
                {view === 'insights' && <InsightsView setStatus={setStatus} />}
                {view === 'calendar' && <CalendarView setStatus={setStatus} />}
                {view === 'reports' && <ReportsView setStatus={setStatus} />}
                {view === 'settings' && <SettingsView setStatus={setStatus} />}
                {view === 'test' && <ApiHealthDashboard />}
            </main>

            {/* Footer */}
            <footer className="bg-white border-t mt-auto">
                <div className="max-w-7xl mx-auto px-4 py-4">
                    <p className="text-center text-sm text-gray-500">
                        Phase 13: Decoupled Architecture Migration
                    </p>
                </div>
            </footer>
        </div>
    )
}

function HabitsView({ setStatus }) {
    const [habits, setHabits] = useState([])
    const [loading, setLoading] = useState(false)
    const [newHabit, setNewHabit] = useState({ name: '', description: '', icon: '🎯' })

    const fetchHabits = async () => {
        setLoading(true)
        try {
            const response = await axios.get(`${API_BASE}/habits`)
            setHabits(response.data.habits)
            setStatus({ type: 'success', message: `Loaded ${response.data.total} habits` })
        } catch (error) {
            setStatus({ type: 'error', message: `Error: ${error.message}` })
        } finally {
            setLoading(false)
        }
    }

    const createHabit = async (e) => {
        e.preventDefault()
        try {
            await axios.post(`${API_BASE}/habits`, newHabit)
            setNewHabit({ name: '', description: '', icon: '🎯' })
            setStatus({ type: 'success', message: 'Habit created!' })
            fetchHabits()
        } catch (error) {
            setStatus({ type: 'error', message: `Error: ${error.message}` })
        }
    }

    const deleteHabit = async (id) => {
        try {
            await axios.delete(`${API_BASE}/habits/${id}`)
            setStatus({ type: 'success', message: 'Habit deleted' })
            fetchHabits()
        } catch (error) {
            setStatus({ type: 'error', message: `Error: ${error.message}` })
        }
    }

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <h2 className="text-xl font-semibold text-gray-900">Habits</h2>
                <button
                    onClick={fetchHabits}
                    disabled={loading}
                    className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:opacity-50"
                >
                    {loading ? 'Loading...' : 'Refresh'}
                </button>
            </div>

            {/* Create Habit Form */}
            <form onSubmit={createHabit} className="bg-white p-4 rounded-lg shadow">
                <div className="flex gap-4">
                    <input
                        type="text"
                        placeholder="Habit name"
                        value={newHabit.name}
                        onChange={(e) => setNewHabit({ ...newHabit, name: e.target.value })}
                        className="flex-1 px-3 py-2 border rounded-md"
                        required
                    />
                    <input
                        type="text"
                        placeholder="Description (optional)"
                        value={newHabit.description}
                        onChange={(e) => setNewHabit({ ...newHabit, description: e.target.value })}
                        className="flex-1 px-3 py-2 border rounded-md"
                    />
                    <button
                        type="submit"
                        className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
                    >
                        Add Habit
                    </button>
                </div>
            </form>

            {/* Habits List */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {habits.map((habit) => (
                    <div key={habit.id} className="bg-white p-4 rounded-lg shadow">
                        <div className="flex items-start justify-between">
                            <div className="flex items-center gap-3">
                                <span className="text-2xl">{habit.icon}</span>
                                <div>
                                    <h3 className="font-medium text-gray-900">{habit.name}</h3>
                                    <p className="text-sm text-gray-500">{habit.description || 'No description'}</p>
                                </div>
                            </div>
                            <button
                                onClick={() => deleteHabit(habit.id)}
                                className="text-red-600 hover:text-red-800 text-sm"
                            >
                                Delete
                            </button>
                        </div>
                        <div className="mt-3 flex gap-2 text-xs text-gray-500">
                            <span className="px-2 py-1 bg-gray-100 rounded">{habit.frequency}</span>
                            <span className="px-2 py-1 bg-gray-100 rounded">{habit.category}</span>
                        </div>
                    </div>
                ))}
            </div>

            {habits.length === 0 && !loading && (
                <p className="text-center text-gray-500 py-8">
                    No habits yet. Create your first habit above!
                </p>
            )}
        </div>
    )
}

function TasksView({ setStatus }) {
    const [tasks, setTasks] = useState([])
    const [loading, setLoading] = useState(false)
    const [newTask, setNewTask] = useState({ title: '', description: '', priority: 'medium' })

    const fetchTasks = async () => {
        setLoading(true)
        try {
            const response = await axios.get(`${API_BASE}/tasks`)
            setTasks(response.data.tasks)
            setStatus({ type: 'success', message: `Loaded ${response.data.total} tasks` })
        } catch (error) {
            setStatus({ type: 'error', message: `Error: ${error.message}` })
        } finally {
            setLoading(false)
        }
    }

    const createTask = async (e) => {
        e.preventDefault()
        try {
            await axios.post(`${API_BASE}/tasks`, newTask)
            setNewTask({ title: '', description: '', priority: 'medium' })
            setStatus({ type: 'success', message: 'Task created!' })
            fetchTasks()
        } catch (error) {
            setStatus({ type: 'error', message: `Error: ${error.message}` })
        }
    }

    const completeTask = async (id) => {
        try {
            await axios.post(`${API_BASE}/tasks/${id}/complete`)
            setStatus({ type: 'success', message: 'Task completed!' })
            fetchTasks()
        } catch (error) {
            setStatus({ type: 'error', message: `Error: ${error.message}` })
        }
    }

    const deleteTask = async (id) => {
        try {
            await axios.delete(`${API_BASE}/tasks/${id}`)
            setStatus({ type: 'success', message: 'Task deleted' })
            fetchTasks()
        } catch (error) {
            setStatus({ type: 'error', message: `Error: ${error.message}` })
        }
    }

    const priorityColors = {
        low: 'bg-blue-100 text-blue-800',
        medium: 'bg-yellow-100 text-yellow-800',
        high: 'bg-orange-100 text-orange-800',
        urgent: 'bg-red-100 text-red-800',
    }

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <h2 className="text-xl font-semibold text-gray-900">Tasks</h2>
                <button
                    onClick={fetchTasks}
                    disabled={loading}
                    className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:opacity-50"
                >
                    {loading ? 'Loading...' : 'Refresh'}
                </button>
            </div>

            {/* Create Task Form */}
            <form onSubmit={createTask} className="bg-white p-4 rounded-lg shadow">
                <div className="flex gap-4">
                    <input
                        type="text"
                        placeholder="Task title"
                        value={newTask.title}
                        onChange={(e) => setNewTask({ ...newTask, title: e.target.value })}
                        className="flex-1 px-3 py-2 border rounded-md"
                        required
                    />
                    <input
                        type="text"
                        placeholder="Description (optional)"
                        value={newTask.description}
                        onChange={(e) => setNewTask({ ...newTask, description: e.target.value })}
                        className="flex-1 px-3 py-2 border rounded-md"
                    />
                    <select
                        value={newTask.priority}
                        onChange={(e) => setNewTask({ ...newTask, priority: e.target.value })}
                        className="px-3 py-2 border rounded-md"
                    >
                        <option value="low">Low</option>
                        <option value="medium">Medium</option>
                        <option value="high">High</option>
                        <option value="urgent">Urgent</option>
                    </select>
                    <button
                        type="submit"
                        className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
                    >
                        Add Task
                    </button>
                </div>
            </form>

            {/* Tasks List */}
            <div className="space-y-2">
                {tasks.map((task) => (
                    <div key={task.id} className={`bg-white p-4 rounded-lg shadow flex items-center justify-between ${task.completed ? 'opacity-60' : ''
                        }`}>
                        <div className="flex items-center gap-3">
                            <button
                                onClick={() => !task.completed && completeTask(task.id)}
                                disabled={task.completed}
                                className={`w-6 h-6 rounded-full border-2 flex items-center justify-center ${task.completed
                                    ? 'bg-green-500 border-green-500 text-white'
                                    : 'border-gray-300 hover:border-green-500'
                                    }`}
                            >
                                {task.completed && '✓'}
                            </button>
                            <div>
                                <h3 className={`font-medium ${task.completed ? 'line-through text-gray-500' : 'text-gray-900'}`}>
                                    {task.title}
                                </h3>
                                <p className="text-sm text-gray-500">{task.description || 'No description'}</p>
                            </div>
                        </div>
                        <div className="flex items-center gap-3">
                            <span className={`px-2 py-1 rounded text-xs ${priorityColors[task.priority] || ''}`}>
                                {task.priority}
                            </span>
                            <button
                                onClick={() => deleteTask(task.id)}
                                className="text-red-600 hover:text-red-800 text-sm"
                            >
                                Delete
                            </button>
                        </div>
                    </div>
                ))}
            </div>

            {tasks.length === 0 && !loading && (
                <p className="text-center text-gray-500 py-8">
                    No tasks yet. Create your first task above!
                </p>
            )}
        </div>
    )
}

function DashboardView({ setStatus }) {
    const [stats, setStats] = useState({
        habits: 0,
        tasks: 0,
        goals: 0,
        healthEntries: 0,
    })
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        const fetchStats = async () => {
            try {
                const [habits, tasks, goals, health] = await Promise.all([
                    axios.get(`${API_BASE}/habits`),
                    axios.get(`${API_BASE}/tasks`),
                    axios.get(`${API_BASE}/goals`),
                    axios.get(`${API_BASE}/health`),
                ])

                setStats({
                    habits: habits.data.total || 0,
                    tasks: tasks.data.total || 0,
                    goals: goals.data.total || 0,
                    healthEntries: health.data.total || 0,
                })
            } catch (error) {
                console.error('Error fetching dashboard stats:', error)
            } finally {
                setLoading(false)
            }
        }

        fetchStats()
    }, [])

    const getGreeting = () => {
        const hour = new Date().getHours()
        if (hour < 12) return '🌅 Good morning'
        if (hour < 17) return '☀️ Good afternoon'
        if (hour < 21) return '🌆 Good evening'
        return '🌙 Time to wind down'
    }

    if (loading) {
        return (
            <div className="text-center py-12">
                <p className="text-gray-500">Loading dashboard...</p>
            </div>
        )
    }

    return (
        <div className="space-y-6">
            {/* Greeting */}
            <div className="bg-gradient-to-r from-primary-500 to-primary-600 rounded-lg shadow-lg p-6 text-white">
                <h2 className="text-3xl font-bold">{getGreeting()}!</h2>
                <p className="mt-2 text-primary-100">Ready to track your progress today?</p>
            </div>

            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="bg-white p-6 rounded-lg shadow">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-gray-500">Habits</p>
                            <p className="text-3xl font-bold text-gray-900">{stats.habits}</p>
                        </div>
                        <div className="text-4xl">🎯</div>
                    </div>
                </div>

                <div className="bg-white p-6 rounded-lg shadow">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-gray-500">Tasks</p>
                            <p className="text-3xl font-bold text-gray-900">{stats.tasks}</p>
                        </div>
                        <div className="text-4xl">📋</div>
                    </div>
                </div>

                <div className="bg-white p-6 rounded-lg shadow">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-gray-500">Goals</p>
                            <p className="text-3xl font-bold text-gray-900">{stats.goals}</p>
                        </div>
                        <div className="text-4xl">🏆</div>
                    </div>
                </div>

                <div className="bg-white p-6 rounded-lg shadow">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-gray-500">Health Logs</p>
                            <p className="text-3xl font-bold text-gray-900">{stats.healthEntries}</p>
                        </div>
                        <div className="text-4xl">❤️</div>
                    </div>
                </div>
            </div>

            {/* Quick Actions */}
            <div className="bg-white p-6 rounded-lg shadow">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <button
                        onClick={() => setStatus({ type: 'info', message: 'Navigate to Habits to add' })}
                        className="p-4 bg-primary-50 text-primary-700 rounded-lg hover:bg-primary-100 transition"
                    >
                        <span className="text-2xl block mb-2">➕</span>
                        <span className="text-sm font-medium">Add Habit</span>
                    </button>
                    <button
                        onClick={() => setStatus({ type: 'info', message: 'Navigate to Tasks to add' })}
                        className="p-4 bg-green-50 text-green-700 rounded-lg hover:bg-green-100 transition"
                    >
                        <span className="text-2xl block mb-2">✓</span>
                        <span className="text-sm font-medium">Complete Task</span>
                    </button>
                    <button
                        onClick={() => setStatus({ type: 'info', message: 'Navigate to Health to log' })}
                        className="p-4 bg-red-50 text-red-700 rounded-lg hover:bg-red-100 transition"
                    >
                        <span className="text-2xl block mb-2">📝</span>
                        <span className="text-sm font-medium">Log Health</span>
                    </button>
                    <button
                        onClick={() => setStatus({ type: 'info', message: 'Navigate to Time to start' })}
                        className="p-4 bg-purple-50 text-purple-700 rounded-lg hover:bg-purple-100 transition"
                    >
                        <span className="text-2xl block mb-2">⏱️</span>
                        <span className="text-sm font-medium">Start Timer</span>
                    </button>
                </div>
            </div>

            {/* Motivation */}
            <div className="bg-white p-6 rounded-lg shadow">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Today's Focus</h3>
                <div className="text-center py-8">
                    <p className="text-gray-600 text-lg">
                        {stats.tasks === 0 && stats.habits === 0
                            ? "🎉 You're all caught up! Time to relax or set new goals."
                            : "💪 Every small step counts. Keep going!"}
                    </p>
                </div>
            </div>
        </div>
    )
}

function GoalsView({ setStatus }) {
    const [goals, setGoals] = useState([])
    const [loading, setLoading] = useState(false)
    const [newGoal, setNewGoal] = useState({
        title: '',
        description: '',
        target: 100,
        current: 0,
        unit: '%',
    })

    const fetchGoals = async () => {
        setLoading(true)
        try {
            const response = await axios.get(`${API_BASE}/goals`)
            setGoals(response.data.goals)
            setStatus({ type: 'success', message: `Loaded ${response.data.total} goals` })
        } catch (error) {
            setStatus({ type: 'error', message: `Error: ${error.message}` })
        } finally {
            setLoading(false)
        }
    }

    const createGoal = async (e) => {
        e.preventDefault()
        try {
            await axios.post(`${API_BASE}/goals`, newGoal)
            setNewGoal({ title: '', description: '', target: 100, current: 0, unit: '%' })
            setStatus({ type: 'success', message: 'Goal created!' })
            fetchGoals()
        } catch (error) {
            setStatus({ type: 'error', message: `Error: ${error.message}` })
        }
    }

    const updateProgress = async (id, newCurrent) => {
        try {
            await axios.put(`${API_BASE}/goals/${id}`, { current: newCurrent })
            setStatus({ type: 'success', message: 'Progress updated!' })
            fetchGoals()
        } catch (error) {
            setStatus({ type: 'error', message: `Error: ${error.message}` })
        }
    }

    const deleteGoal = async (id) => {
        try {
            await axios.delete(`${API_BASE}/goals/${id}`)
            setStatus({ type: 'success', message: 'Goal deleted' })
            fetchGoals()
        } catch (error) {
            setStatus({ type: 'error', message: `Error: ${error.message}` })
        }
    }

    const calculateProgress = (current, target) => {
        if (!target || target === 0) return 0
        return Math.min(100, Math.round((current / target) * 100))
    }

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <h2 className="text-xl font-semibold text-gray-900">Goals</h2>
                <button
                    onClick={fetchGoals}
                    disabled={loading}
                    className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:opacity-50"
                >
                    {loading ? 'Loading...' : 'Refresh'}
                </button>
            </div>

            {/* Create Goal Form */}
            <form onSubmit={createGoal} className="bg-white p-4 rounded-lg shadow">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <input
                        type="text"
                        placeholder="Goal title"
                        value={newGoal.title}
                        onChange={(e) => setNewGoal({ ...newGoal, title: e.target.value })}
                        className="px-3 py-2 border rounded-md"
                        required
                    />
                    <input
                        type="text"
                        placeholder="Description (optional)"
                        value={newGoal.description}
                        onChange={(e) => setNewGoal({ ...newGoal, description: e.target.value })}
                        className="px-3 py-2 border rounded-md"
                    />
                    <div className="flex gap-2">
                        <input
                            type="number"
                            placeholder="Target"
                            value={newGoal.target}
                            onChange={(e) => setNewGoal({ ...newGoal, target: parseFloat(e.target.value) || 0 })}
                            className="flex-1 px-3 py-2 border rounded-md"
                        />
                        <input
                            type="text"
                            placeholder="Unit"
                            value={newGoal.unit}
                            onChange={(e) => setNewGoal({ ...newGoal, unit: e.target.value })}
                            className="w-24 px-3 py-2 border rounded-md"
                        />
                    </div>
                    <button
                        type="submit"
                        className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
                    >
                        Create Goal
                    </button>
                </div>
            </form>

            {/* Goals List */}
            <div className="grid gap-4">
                {goals.map((goal) => (
                    <div key={goal.id} className="bg-white p-4 rounded-lg shadow">
                        <div className="flex items-start justify-between mb-3">
                            <div className="flex-1">
                                <h3 className="font-medium text-gray-900">{goal.title}</h3>
                                <p className="text-sm text-gray-500">{goal.description || 'No description'}</p>
                            </div>
                            <button
                                onClick={() => deleteGoal(goal.id)}
                                className="text-red-600 hover:text-red-800 text-sm"
                            >
                                Delete
                            </button>
                        </div>

                        {/* Progress Bar */}
                        <div className="mb-3">
                            <div className="flex justify-between text-sm mb-1">
                                <span className="text-gray-600">Progress</span>
                                <span className="font-medium">
                                    {goal.current} / {goal.target} {goal.unit}
                                </span>
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-3">
                                <div
                                    className={`h-3 rounded-full transition-all ${goal.completed ? 'bg-green-500' : 'bg-primary-500'
                                        }`}
                                    style={{ width: `${calculateProgress(goal.current, goal.target)}%` }}
                                />
                            </div>
                        </div>

                        {/* Update Progress */}
                        <div className="flex gap-2">
                            <input
                                type="number"
                                placeholder="New current"
                                onChange={(e) => {
                                    const val = parseFloat(e.target.value)
                                    if (!isNaN(val)) updateProgress(goal.id, val)
                                }}
                                className="flex-1 px-3 py-1 text-sm border rounded-md"
                            />
                            <span className="text-sm text-gray-500 py-1">{goal.unit}</span>
                        </div>

                        {/* Status Badge */}
                        <div className="mt-3">
                            {goal.completed ? (
                                <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                                    ✓ Completed
                                </span>
                            ) : (
                                <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                                    🎯 In Progress
                                </span>
                            )}
                        </div>
                    </div>
                ))}
            </div>

            {goals.length === 0 && !loading && (
                <div className="text-center py-12 bg-white rounded-lg shadow">
                    <p className="text-gray-500">No goals yet. Create your first goal above!</p>
                </div>
            )}
        </div>
    )
}

function HealthView({ setStatus }) {
    const [entries, setEntries] = useState([])
    const [loading, setLoading] = useState(false)
    const [newEntry, setNewEntry] = useState({
        entry_date: new Date().toISOString().split('T')[0],
        weight: '',
        sleep_hours: '',
        mood: 'good',
        notes: '',
    })

    const fetchEntries = async () => {
        setLoading(true)
        try {
            const response = await axios.get(`${API_BASE}/health`)
            setEntries(response.data.entries)
            setStatus({ type: 'success', message: `Loaded ${response.data.total} entries` })
        } catch (error) {
            setStatus({ type: 'error', message: `Error: ${error.message}` })
        } finally {
            setLoading(false)
        }
    }

    const createEntry = async (e) => {
        e.preventDefault()
        try {
            await axios.post(`${API_BASE}/health`, {
                ...newEntry,
                weight: newEntry.weight ? parseFloat(newEntry.weight) : null,
                sleep_hours: newEntry.sleep_hours ? parseFloat(newEntry.sleep_hours) : null,
            })
            setNewEntry({
                entry_date: new Date().toISOString().split('T')[0],
                weight: '',
                sleep_hours: '',
                mood: 'good',
                notes: '',
            })
            setStatus({ type: 'success', message: 'Health entry created!' })
            fetchEntries()
        } catch (error) {
            setStatus({ type: 'error', message: `Error: ${error.message}` })
        }
    }

    const deleteEntry = async (id) => {
        try {
            await axios.delete(`${API_BASE}/health/${id}`)
            setStatus({ type: 'success', message: 'Entry deleted' })
            fetchEntries()
        } catch (error) {
            setStatus({ type: 'error', message: `Error: ${error.message}` })
        }
    }

    const moodEmojis = {
        bad: '😢',
        poor: '😕',
        good: '🙂',
        great: '😄',
    }

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <h2 className="text-xl font-semibold text-gray-900">Health Tracking</h2>
                <button
                    onClick={fetchEntries}
                    disabled={loading}
                    className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:opacity-50"
                >
                    {loading ? 'Loading...' : 'Refresh'}
                </button>
            </div>

            {/* Create Entry Form */}
            <form onSubmit={createEntry} className="bg-white p-4 rounded-lg shadow">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    <input
                        type="date"
                        value={newEntry.entry_date}
                        onChange={(e) => setNewEntry({ ...newEntry, entry_date: e.target.value })}
                        className="px-3 py-2 border rounded-md"
                    />
                    <input
                        type="number"
                        placeholder="Weight (kg/lbs)"
                        value={newEntry.weight}
                        onChange={(e) => setNewEntry({ ...newEntry, weight: e.target.value })}
                        className="px-3 py-2 border rounded-md"
                        step="0.1"
                    />
                    <input
                        type="number"
                        placeholder="Sleep (hours)"
                        value={newEntry.sleep_hours}
                        onChange={(e) => setNewEntry({ ...newEntry, sleep_hours: e.target.value })}
                        className="px-3 py-2 border rounded-md"
                        step="0.5"
                        min="0"
                        max="24"
                    />
                    <select
                        value={newEntry.mood}
                        onChange={(e) => setNewEntry({ ...newEntry, mood: e.target.value })}
                        className="px-3 py-2 border rounded-md"
                    >
                        <option value="bad">😢 Bad</option>
                        <option value="poor">😕 Poor</option>
                        <option value="good">🙂 Good</option>
                        <option value="great">😄 Great</option>
                    </select>
                    <input
                        type="text"
                        placeholder="Notes (optional)"
                        value={newEntry.notes}
                        onChange={(e) => setNewEntry({ ...newEntry, notes: e.target.value })}
                        className="lg:col-span-2 px-3 py-2 border rounded-md"
                    />
                    <button
                        type="submit"
                        className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
                    >
                        Add Entry
                    </button>
                </div>
            </form>

            {/* Health Entries List */}
            <div className="bg-white rounded-lg shadow overflow-hidden">
                <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                        <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Weight</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Sleep</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Mood</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Notes</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                        </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                        {entries.map((entry) => (
                            <tr key={entry.id}>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{entry.entry_date}</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                    {entry.weight ? `${entry.weight}` : '-'}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                    {entry.sleep_hours ? `${entry.sleep_hours}h` : '-'}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm">
                                    <span className="text-xl">{moodEmojis[entry.mood]}</span>
                                </td>
                                <td className="px-6 py-4 text-sm text-gray-500 max-w-xs truncate">
                                    {entry.notes || '-'}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm">
                                    <button
                                        onClick={() => deleteEntry(entry.id)}
                                        className="text-red-600 hover:text-red-800"
                                    >
                                        Delete
                                    </button>
                                </td>
                            </tr>
                        ))}
                        {entries.length === 0 && (
                            <tr>
                                <td colSpan="6" className="px-6 py-8 text-center text-gray-500">
                                    No health entries yet. Start tracking your health!
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    )
}

function TimeView({ setStatus }) {
    const [entries, setEntries] = useState([])
    const [categories, setCategories] = useState([])
    const [loading, setLoading] = useState(false)
    const [newEntry, setNewEntry] = useState({ category: 'General', duration_seconds: 3600, notes: '' })

    const fetchEntries = async () => {
        setLoading(true)
        try {
            const response = await axios.get(`${API_BASE}/time/entries`)
            setEntries(response.data)
            setStatus({ type: 'success', message: `Loaded ${response.data.length} time entries` })
        } catch (error) {
            setStatus({ type: 'error', message: `Error: ${error.message}` })
        } finally {
            setLoading(false)
        }
    }

    const fetchCategories = async () => {
        try {
            const response = await axios.get(`${API_BASE}/time/categories`)
            setCategories(response.data)
            setNewEntry({ ...newEntry, category: response.data[0] })
        } catch (error) {
            console.error('Error fetching categories:', error)
        }
    }

    const createEntry = async (e) => {
        e.preventDefault()
        try {
            await axios.post(`${API_BASE}/time/entries`, newEntry)
            setNewEntry({ category: categories[0] || 'General', duration_seconds: 3600, notes: '' })
            setStatus({ type: 'success', message: 'Time entry created!' })
            fetchEntries()
        } catch (error) {
            setStatus({ type: 'error', message: `Error: ${error.message}` })
        }
    }

    const formatDuration = (seconds) => {
        const hours = Math.floor(seconds / 3600)
        const mins = Math.floor((seconds % 3600) / 60)
        return `${hours}h ${mins}m`
    }

    useEffect(() => {
        fetchCategories()
        fetchEntries()
    }, [])

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <h2 className="text-xl font-semibold text-gray-900">Time Tracking</h2>
                <button
                    onClick={fetchEntries}
                    disabled={loading}
                    className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:opacity-50"
                >
                    {loading ? 'Loading...' : 'Refresh'}
                </button>
            </div>

            {/* Create Entry Form */}
            <form onSubmit={createEntry} className="bg-white p-4 rounded-lg shadow">
                <div className="flex gap-4 flex-wrap">
                    <select
                        value={newEntry.category}
                        onChange={(e) => setNewEntry({ ...newEntry, category: e.target.value })}
                        className="px-3 py-2 border rounded-md"
                    >
                        {categories.map(cat => (
                            <option key={cat} value={cat}>{cat}</option>
                        ))}
                    </select>
                    <input
                        type="number"
                        placeholder="Duration (seconds)"
                        value={newEntry.duration_seconds}
                        onChange={(e) => setNewEntry({ ...newEntry, duration_seconds: parseInt(e.target.value) || 0 })}
                        className="px-3 py-2 border rounded-md w-40"
                        min="60"
                    />
                    <input
                        type="text"
                        placeholder="Notes (optional)"
                        value={newEntry.notes}
                        onChange={(e) => setNewEntry({ ...newEntry, notes: e.target.value })}
                        className="flex-1 px-3 py-2 border rounded-md"
                    />
                    <button
                        type="submit"
                        className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
                    >
                        Add Entry
                    </button>
                </div>
            </form>

            {/* Time Entries List */}
            <div className="bg-white rounded-lg shadow overflow-hidden">
                <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                        <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Category</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Duration</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Notes</th>
                        </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                        {entries.map(entry => (
                            <tr key={entry.id}>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{entry.entry_date}</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{entry.category}</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{formatDuration(entry.duration_seconds)}</td>
                                <td className="px-6 py-4 text-sm text-gray-500">{entry.notes || '-'}</td>
                            </tr>
                        ))}
                        {entries.length === 0 && (
                            <tr>
                                <td colSpan="4" className="px-6 py-8 text-center text-gray-500">
                                    No time entries yet. Start tracking your time!
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    )
}

function FinancesView({ setStatus }) {
    const [transactions, setTransactions] = useState([])
    const [summary, setSummary] = useState(null)
    const [loading, setLoading] = useState(false)
    const [newTransaction, setNewTransaction] = useState({
        description: '',
        amount: 0,
        type: 'expense',
        category: 'Food'
    })

    const fetchTransactions = async () => {
        setLoading(true)
        try {
            const response = await axios.get(`${API_BASE}/finances/transactions`)
            setTransactions(response.data)
            setStatus({ type: 'success', message: `Loaded ${response.data.length} transactions` })
        } catch (error) {
            setStatus({ type: 'error', message: `Error: ${error.message}` })
        } finally {
            setLoading(false)
        }
    }

    const fetchSummary = async () => {
        try {
            const response = await axios.get(`${API_BASE}/finances/summary`)
            setSummary(response.data)
        } catch (error) {
            console.error('Error fetching summary:', error)
        }
    }

    const createTransaction = async (e) => {
        e.preventDefault()
        try {
            await axios.post(`${API_BASE}/finances/transactions`, newTransaction)
            setNewTransaction({ description: '', amount: 0, type: 'expense', category: 'Food' })
            setStatus({ type: 'success', message: 'Transaction created!' })
            fetchTransactions()
            fetchSummary()
        } catch (error) {
            setStatus({ type: 'error', message: `Error: ${error.message}` })
        }
    }

    useEffect(() => {
        fetchTransactions()
        fetchSummary()
    }, [])

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <h2 className="text-xl font-semibold text-gray-900">Finances</h2>
                <button
                    onClick={() => { fetchTransactions(); fetchSummary(); }}
                    disabled={loading}
                    className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:opacity-50"
                >
                    {loading ? 'Loading...' : 'Refresh'}
                </button>
            </div>

            {/* Summary Cards */}
            {summary && (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="bg-white p-4 rounded-lg shadow">
                        <h3 className="text-sm font-medium text-gray-500">Total Income</h3>
                        <p className="text-2xl font-bold text-green-600">${summary.total_income.toFixed(2)}</p>
                    </div>
                    <div className="bg-white p-4 rounded-lg shadow">
                        <h3 className="text-sm font-medium text-gray-500">Total Expenses</h3>
                        <p className="text-2xl font-bold text-red-600">${summary.total_expenses.toFixed(2)}</p>
                    </div>
                    <div className="bg-white p-4 rounded-lg shadow">
                        <h3 className="text-sm font-medium text-gray-500">Net</h3>
                        <p className={`text-2xl font-bold ${summary.net >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            ${summary.net.toFixed(2)}
                        </p>
                    </div>
                </div>
            )}

            {/* Create Transaction Form */}
            <form onSubmit={createTransaction} className="bg-white p-4 rounded-lg shadow">
                <div className="flex gap-4 flex-wrap">
                    <input
                        type="text"
                        placeholder="Description"
                        value={newTransaction.description}
                        onChange={(e) => setNewTransaction({ ...newTransaction, description: e.target.value })}
                        className="flex-1 px-3 py-2 border rounded-md"
                        required
                    />
                    <input
                        type="number"
                        placeholder="Amount"
                        value={newTransaction.amount}
                        onChange={(e) => setNewTransaction({ ...newTransaction, amount: parseFloat(e.target.value) || 0 })}
                        className="px-3 py-2 border rounded-md w-32"
                        min="0.01"
                        step="0.01"
                    />
                    <select
                        value={newTransaction.type}
                        onChange={(e) => setNewTransaction({ ...newTransaction, type: e.target.value })}
                        className="px-3 py-2 border rounded-md"
                    >
                        <option value="income">Income</option>
                        <option value="expense">Expense</option>
                    </select>
                    <input
                        type="text"
                        placeholder="Category"
                        value={newTransaction.category}
                        onChange={(e) => setNewTransaction({ ...newTransaction, category: e.target.value })}
                        className="px-3 py-2 border rounded-md w-32"
                    />
                    <button
                        type="submit"
                        className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
                    >
                        Add
                    </button>
                </div>
            </form>

            {/* Transactions List */}
            <div className="bg-white rounded-lg shadow overflow-hidden">
                <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                        <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Description</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Category</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Amount</th>
                        </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                        {transactions.map(tx => (
                            <tr key={tx.id}>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{tx.trans_date}</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{tx.description}</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{tx.category || '-'}</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm">
                                    <span className={`px-2 py-1 rounded-full text-xs ${tx.type === 'income' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                                        {tx.type}
                                    </span>
                                </td>
                                <td className={`px-6 py-4 whitespace-nowrap text-sm font-medium ${tx.type === 'income' ? 'text-green-600' : 'text-red-600'}`}>
                                    {tx.type === 'income' ? '+' : '-'}${tx.amount.toFixed(2)}
                                </td>
                            </tr>
                        ))}
                        {transactions.length === 0 && (
                            <tr>
                                <td colSpan="5" className="px-6 py-8 text-center text-gray-500">
                                    No transactions yet. Add your first one!
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    )
}

// Emotional Health View (RGB Model: Dopamine, Norepinephrine, Serotonin)
function EmotionalHealthView({ setStatus }) {
    const [entries, setEntries] = useState([])
    const [loading, setLoading] = useState(false)
    const [newEntry, setNewEntry] = useState({
        dopamine: 50, // Joy/Excitement
        norepinephrine: 50, // Stress/Energy
        serotonin: 50, // Satisfaction/Calm
        mood: 'neutral',
        notes: ''
    })

    const EMOTION_PRESETS = [
        { name: 'Joyful', dopamine: 90, norepinephrine: 60, serotonin: 80, emoji: '😊' },
        { name: 'Excited', dopamine: 95, norepinephrine: 90, serotonin: 60, emoji: '🤩' },
        { name: 'Content', dopamine: 60, norepinephrine: 30, serotonin: 90, emoji: '😌' },
        { name: 'Calm', dopamine: 40, norepinephrine: 20, serotonin: 85, emoji: '😴' },
        { name: 'Anxious', dopamine: 30, norepinephrine: 90, serotonin: 30, emoji: '😰' },
        { name: 'Stressed', dopamine: 20, norepinephrine: 95, serotonin: 20, emoji: '😫' },
        { name: 'Sad', dopamine: 20, norepinephrine: 40, serotonin: 20, emoji: '😢' },
        { name: 'Angry', dopamine: 30, norepinephrine: 85, serotonin: 15, emoji: '😠' },
        { name: 'Tired', dopamine: 30, norepinephrine: 20, serotonin: 40, emoji: '😪' },
        { name: 'Energetic', dopamine: 70, norepinephrine: 70, serotonin: 50, emoji: '⚡' },
        { name: 'Grateful', dopamine: 70, norepinephrine: 30, serotonin: 85, emoji: '🙏' },
        { name: 'Motivated', dopamine: 85, norepinephrine: 70, serotonin: 60, emoji: '💪' },
        { name: 'Frustrated', dopamine: 25, norepinephrine: 80, serotonin: 25, emoji: '😤' },
        { name: 'Bored', dopamine: 20, norepinephrine: 20, serotonin: 40, emoji: '😑' },
        { name: 'Hopeful', dopamine: 70, norepinephrine: 50, serotonin: 65, emoji: '🌟' }
    ]

    const fetchEntries = async () => {
        setLoading(true)
        try {
            const response = await axios.get(`${API_BASE}/emotional-health/entries`)
            setEntries(response.data)
            setStatus({ type: 'success', message: `Loaded ${response.data.length} emotional entries` })
        } catch (error) {
            setStatus({ type: 'error', message: `Error: ${error.message}` })
        } finally {
            setLoading(false)
        }
    }

    const createEntry = async (e) => {
        e.preventDefault()
        try {
            await axios.post(`${API_BASE}/emotional-health/entries`, newEntry)
            setNewEntry({ dopamine: 50, norepinephrine: 50, serotonin: 50, mood: 'neutral', notes: '' })
            setStatus({ type: 'success', message: 'Emotional state recorded!' })
            fetchEntries()
        } catch (error) {
            setStatus({ type: 'error', message: `Error: ${error.message}` })
        }
    }

    const applyPreset = (preset) => {
        setNewEntry({
            ...newEntry,
            dopamine: preset.dopamine,
            norepinephrine: preset.norepinephrine,
            serotonin: preset.serotonin,
            mood: preset.name.toLowerCase()
        })
        setStatus({ type: 'success', message: `Applied ${preset.name} preset` })
    }

    useEffect(() => {
        fetchEntries()
    }, [])

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <h2 className="text-xl font-semibold text-gray-900">Emotional Health</h2>
                <button onClick={fetchEntries} disabled={loading} className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:opacity-50">
                    {loading ? 'Loading...' : 'Refresh'}
                </button>
            </div>

            {/* RGB Sliders */}
            <form onSubmit={createEntry} className="bg-white p-6 rounded-lg shadow">
                <h3 className="text-lg font-medium mb-4">How are you feeling?</h3>

                {/* Presets */}
                <div className="mb-4">
                    <p className="text-sm text-gray-500 mb-2">Quick presets:</p>
                    <div className="flex flex-wrap gap-2">
                        {EMOTION_PRESETS.slice(0, 8).map((preset) => (
                            <button
                                key={preset.name}
                                type="button"
                                onClick={() => applyPreset(preset)}
                                className="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 rounded-full"
                            >
                                {preset.emoji} {preset.name}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Dopamine Slider */}
                <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                        Dopamine (Joy/Excitement): {newEntry.dopamine}%
                    </label>
                    <input
                        type="range"
                        min="0"
                        max="100"
                        value={newEntry.dopamine}
                        onChange={(e) => setNewEntry({ ...newEntry, dopamine: parseInt(e.target.value) })}
                        className="w-full h-2 bg-gradient-to-r from-gray-300 via-purple-500 to-purple-600 rounded-lg appearance-none cursor-pointer"
                    />
                </div>

                {/* Norepinephrine Slider */}
                <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                        Norepinephrine (Stress/Energy): {newEntry.norepinephrine}%
                    </label>
                    <input
                        type="range"
                        min="0"
                        max="100"
                        value={newEntry.norepinephrine}
                        onChange={(e) => setNewEntry({ ...newEntry, norepinephrine: parseInt(e.target.value) })}
                        className="w-full h-2 bg-gradient-to-r from-gray-300 via-red-500 to-red-600 rounded-lg appearance-none cursor-pointer"
                    />
                </div>

                {/* Serotonin Slider */}
                <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                        Serotonin (Satisfaction/Calm): {newEntry.serotonin}%
                    </label>
                    <input
                        type="range"
                        min="0"
                        max="100"
                        value={newEntry.serotonin}
                        onChange={(e) => setNewEntry({ ...newEntry, serotonin: parseInt(e.target.value) })}
                        className="w-full h-2 bg-gradient-to-r from-gray-300 via-blue-500 to-blue-600 rounded-lg appearance-none cursor-pointer"
                    />
                </div>

                <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-1">Notes</label>
                    <input
                        type="text"
                        value={newEntry.notes}
                        onChange={(e) => setNewEntry({ ...newEntry, notes: e.target.value })}
                        placeholder="Any thoughts or context..."
                        className="w-full px-3 py-2 border border-gray-300 rounded-md"
                    />
                </div>

                <button type="submit" className="w-full px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700">
                    Record Emotional State
                </button>
            </form>

            {/* Recent Entries */}
            <div className="bg-white rounded-lg shadow overflow-hidden">
                <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                        <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Dopamine</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Norepinephrine</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Serotonin</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Notes</th>
                        </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                        {entries.slice(0, 10).map((entry) => (
                            <tr key={entry.id}>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{entry.date || '-'}</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm">
                                    <span className="px-2 py-1 rounded-full bg-purple-100 text-purple-800">{entry.dopamine}%</span>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm">
                                    <span className="px-2 py-1 rounded-full bg-red-100 text-red-800">{entry.norepinephrine}%</span>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm">
                                    <span className="px-2 py-1 rounded-full bg-blue-100 text-blue-800">{entry.serotonin}%</span>
                                </td>
                                <td className="px-6 py-4 text-sm text-gray-500 max-w-xs truncate">{entry.notes || '-'}</td>
                            </tr>
                        ))}
                        {entries.length === 0 && (
                            <tr>
                                <td colSpan="5" className="px-6 py-8 text-center text-gray-500">
                                    No emotional entries yet. Start tracking your feelings!
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    )
}

// Achievements View (XP, Levels, Badges)
function AchievementsView({ setStatus }) {
    const [achievements, setAchievements] = useState([])
    const [userStats, setUserStats] = useState(null)
    const [loading, setLoading] = useState(false)

    const fetchData = async () => {
        setLoading(true)
        try {
            const [achievementsRes, statsRes] = await Promise.all([
                axios.get(`${API_BASE}/achievements`),
                axios.get(`${API_BASE}/user/stats`)
            ])
            setAchievements(achievementsRes.data.achievements || [])
            setUserStats(statsRes.data)
            setStatus({ type: 'success', message: 'Achievements loaded!' })
        } catch (error) {
            setStatus({ type: 'error', message: `Error: ${error.message}` })
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        fetchData()
    }, [])

    const getLevelProgress = () => {
        if (!userStats) return 0
        const { xp = 0, level = 1 } = userStats
        const xpForNextLevel = level * 1000
        const xpInCurrentLevel = xp % xpForNextLevel
        return Math.min((xpInCurrentLevel / xpForNextLevel) * 100, 100)
    }

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <h2 className="text-xl font-semibold text-gray-900">Achievements</h2>
                <button onClick={fetchData} disabled={loading} className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:opacity-50">
                    {loading ? 'Loading...' : 'Refresh'}
                </button>
            </div>

            {/* User Stats Card */}
            {userStats && (
                <div className="bg-white p-6 rounded-lg shadow">
                    <div className="flex items-center justify-between mb-4">
                        <div>
                            <h3 className="text-2xl font-bold text-primary-600">Level {userStats.level || 1}</h3>
                            <p className="text-gray-500">{userStats.xp || 0} XP</p>
                        </div>
                        <div className="text-right">
                            <p className="text-sm text-gray-500">Next Level</p>
                            <p className="font-medium">{((userStats.level || 1) * 1000) - (userStats.xp || 0)} XP away</p>
                        </div>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-4">
                        <div
                            className="bg-primary-600 h-4 rounded-full transition-all duration-500"
                            style={{ width: `${getLevelProgress()}%` }}
                        />
                    </div>
                </div>
            )}

            {/* Achievement Badges */}
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                {achievements.map((achievement) => (
                    <div
                        key={achievement.id}
                        className={`p-4 rounded-lg shadow ${achievement.unlocked ? 'bg-white' : 'bg-gray-100 opacity-60'}`}
                    >
                        <div className="text-4xl mb-2 text-center">{achievement.icon || '🏆'}</div>
                        <h4 className="font-medium text-center">{achievement.name}</h4>
                        <p className="text-sm text-gray-500 text-center mt-1">{achievement.description}</p>
                        {achievement.unlocked && (
                            <p className="text-xs text-green-600 text-center mt-2">✓ Unlocked</p>
                        )}
                    </div>
                ))}
                {achievements.length === 0 && (
                    <div className="col-span-full text-center py-8 text-gray-500">
                        No achievements yet. Complete habits to earn badges!
                    </div>
                )}
            </div>
        </div>
    )
}

// Insights View (AI-Powered Analytics)
function InsightsView({ setStatus }) {
    const [insights, setInsights] = useState([])
    const [correlations, setCorrelations] = useState([])
    const [burnoutRisk, setBurnoutRisk] = useState(null)
    const [loading, setLoading] = useState(false)

    const fetchData = async () => {
        setLoading(true)
        try {
            const [insightsRes] = await Promise.all([
                axios.get(`${API_BASE}/insights`)
            ])
            setInsights(insightsRes.data.insights || [])
            setCorrelations(insightsRes.data.correlations || [])
            setBurnoutRisk(insightsRes.data.burnout_risk)
            setStatus({ type: 'success', message: 'Insights loaded!' })
        } catch (error) {
            setStatus({ type: 'error', message: `Error: ${error.message}` })
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        fetchData()
    }, [])

    const getBurnoutColor = (risk) => {
        if (risk === null || risk === undefined) return 'bg-gray-100'
        if (risk < 30) return 'bg-green-100 text-green-800'
        if (risk < 60) return 'bg-yellow-100 text-yellow-800'
        if (risk < 80) return 'bg-orange-100 text-orange-800'
        return 'bg-red-100 text-red-800'
    }

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <h2 className="text-xl font-semibold text-gray-900">Insights</h2>
                <button onClick={fetchData} disabled={loading} className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:opacity-50">
                    {loading ? 'Loading...' : 'Refresh'}
                </button>
            </div>

            {/* Burnout Risk Card */}
            {burnoutRisk !== null && burnoutRisk !== undefined && (
                <div className={`p-6 rounded-lg shadow ${getBurnoutColor(burnoutRisk)}`}>
                    <h3 className="text-lg font-semibold mb-2">🔥 Burnout Risk Level</h3>
                    <div className="flex items-center gap-4">
                        <span className="text-4xl font-bold">{burnoutRisk}%</span>
                        <div className="flex-1">
                            <div className="w-full bg-gray-300 rounded-full h-3">
                                <div
                                    className={`h-3 rounded-full ${burnoutRisk < 30 ? 'bg-green-500' : burnoutRisk < 60 ? 'bg-yellow-500' : burnoutRisk < 80 ? 'bg-orange-500' : 'bg-red-500'}`}
                                    style={{ width: `${burnoutRisk}%` }}
                                />
                            </div>
                        </div>
                    </div>
                    {burnoutRisk >= 60 && (
                        <p className="mt-2 text-sm">Consider taking a break or reducing habit load.</p>
                    )}
                </div>
            )}

            {/* AI Insights */}
            <div className="bg-white rounded-lg shadow overflow-hidden">
                <div className="px-6 py-4 border-b">
                    <h3 className="text-lg font-semibold">💡 AI Insights</h3>
                </div>
                <div className="p-6">
                    {insights.length > 0 ? (
                        <div className="space-y-4">
                            {insights.map((insight, idx) => (
                                <div key={idx} className="flex gap-3 p-3 bg-blue-50 rounded-lg">
                                    <span className="text-xl">💡</span>
                                    <div>
                                        <p className="font-medium">{insight.title}</p>
                                        <p className="text-sm text-gray-600">{insight.description}</p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <p className="text-gray-500 text-center py-4">No insights available yet. Keep tracking!</p>
                    )}
                </div>
            </div>

            {/* Correlations */}
            <div className="bg-white rounded-lg shadow overflow-hidden">
                <div className="px-6 py-4 border-b">
                    <h3 className="text-lg font-semibold">🔗 Correlations</h3>
                </div>
                <div className="p-6">
                    {correlations.length > 0 ? (
                        <div className="space-y-3">
                            {correlations.map((corr, idx) => (
                                <div key={idx} className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                                    <span className="text-sm">{corr.factor_1} ↔ {corr.factor_2}</span>
                                    <span className={`px-2 py-1 rounded text-xs font-medium ${corr.strength > 0.5 ? 'bg-green-100 text-green-800' :
                                        corr.strength > 0.3 ? 'bg-yellow-100 text-yellow-800' :
                                            'bg-gray-100 text-gray-800'
                                        }`}>
                                        {corr.strength.toFixed(2)}
                                    </span>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <p className="text-gray-500 text-center py-4">No correlations detected yet.</p>
                    )}
                </div>
            </div>
        </div>
    )
}

// Calendar View with Habit Heatmap
function CalendarView({ setStatus }) {
    const [currentDate, setCurrentDate] = useState(new Date())
    const [habits, setHabits] = useState([])
    const [entries, setEntries] = useState({})
    const [loading, setLoading] = useState(false)

    const fetchData = async () => {
        setLoading(true)
        try {
            const [habitsRes, entriesRes] = await Promise.all([
                axios.get(`${API_BASE}/habits`),
                axios.get(`${API_BASE}/habits/entries`)
            ])
            setHabits(habitsRes.data)
            // Organize entries by date
            const entryMap = {}
            entriesRes.data.forEach(entry => {
                const date = entry.date
                if (!entryMap[date]) entryMap[date] = []
                entryMap[date].push(entry)
            })
            setEntries(entryMap)
            setStatus({ type: 'success', message: 'Calendar data loaded!' })
        } catch (error) {
            setStatus({ type: 'error', message: `Error: ${error.message}` })
        } finally {
            setLoading(false)
        }
    }

    const getDaysInMonth = (date) => {
        const year = date.getFullYear()
        const month = date.getMonth()
        return new Date(year, month + 1, 0).getDate()
    }

    const getFirstDayOfMonth = (date) => {
        const year = date.getFullYear()
        const month = date.getMonth()
        return new Date(year, month, 1).getDay()
    }

    const formatDate = (day) => {
        const year = currentDate.getFullYear()
        const month = String(currentDate.getMonth() + 1).padStart(2, '0')
        const dayStr = String(day).padStart(2, '0')
        return `${year}-${month}-${dayStr}`
    }

    const prevMonth = () => {
        setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1, 1))
    }

    const nextMonth = () => {
        setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 1))
    }

    const getCompletionColor = (day) => {
        const dateStr = formatDate(day)
        const dayEntries = entries[dateStr] || []
        if (dayEntries.length === 0) return 'bg-gray-50'
        const rate = dayEntries.length / habits.length
        if (rate >= 0.8) return 'bg-green-500'
        if (rate >= 0.5) return 'bg-green-300'
        if (rate >= 0.3) return 'bg-yellow-300'
        return 'bg-yellow-100'
    }

    useEffect(() => {
        fetchData()
    }, [])

    const daysInMonth = getDaysInMonth(currentDate)
    const firstDay = getFirstDayOfMonth(currentDate)
    const days = []
    for (let i = 0; i < firstDay; i++) days.push(null)
    for (let i = 1; i <= daysInMonth; i++) days.push(i)

    const monthNames = ['January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December']

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <h2 className="text-xl font-semibold text-gray-900">Calendar</h2>
                <button onClick={fetchData} disabled={loading} className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:opacity-50">
                    {loading ? 'Loading...' : 'Refresh'}
                </button>
            </div>

            {/* Month Navigation */}
            <div className="bg-white p-4 rounded-lg shadow">
                <div className="flex justify-between items-center mb-4">
                    <button onClick={prevMonth} className="px-4 py-2 bg-gray-100 rounded hover:bg-gray-200">← Prev</button>
                    <h3 className="text-lg font-semibold">{monthNames[currentDate.getMonth()]} {currentDate.getFullYear()}</h3>
                    <button onClick={nextMonth} className="px-4 py-2 bg-gray-100 rounded hover:bg-gray-200">Next →</button>
                </div>

                {/* Calendar Grid */}
                <div className="grid grid-cols-7 gap-1">
                    {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
                        <div key={day} className="text-center text-sm font-medium text-gray-500 py-2">{day}</div>
                    ))}
                    {days.map((day, idx) => (
                        <div
                            key={idx}
                            className={`h-16 border rounded flex items-center justify-center text-sm ${day ? `${getCompletionColor(day)} cursor-pointer hover:opacity-80` : ''
                                }`}
                        >
                            {day}
                        </div>
                    ))}
                </div>
            </div>

            {/* Legend */}
            <div className="bg-white p-4 rounded-lg shadow">
                <h4 className="text-sm font-medium mb-2">Completion Legend</h4>
                <div className="flex gap-4 text-sm">
                    <div className="flex items-center gap-1"><div className="w-4 h-4 bg-green-500 rounded"></div> 80%+</div>
                    <div className="flex items-center gap-1"><div className="w-4 h-4 bg-green-300 rounded"></div> 50-79%</div>
                    <div className="flex items-center gap-1"><div className="w-4 h-4 bg-yellow-300 rounded"></div> 30-49%</div>
                    <div className="flex items-center gap-1"><div className="w-4 h-4 bg-yellow-100 rounded"></div> 1-29%</div>
                    <div className="flex items-center gap-1"><div className="w-4 h-4 bg-gray-50 border rounded"></div> None</div>
                </div>
            </div>
        </div>
    )
}

// Reports View with Date Range and Export
function ReportsView({ setStatus }) {
    const [dateRange, setDateRange] = useState('week')
    const [startDate, setStartDate] = useState('')
    const [endDate, setEndDate] = useState('')
    const [reportData, setReportData] = useState(null)
    const [loading, setLoading] = useState(false)

    const fetchReport = async () => {
        setLoading(true)
        try {
            const params = new URLSearchParams()
            if (dateRange === 'custom') {
                if (startDate) params.append('start_date', startDate)
                if (endDate) params.append('end_date', endDate)
            } else {
                params.append('range', dateRange)
            }
            const response = await axios.get(`${API_BASE}/habits/report?${params}`)
            setReportData(response.data)
            setStatus({ type: 'success', message: 'Report loaded!' })
        } catch (error) {
            setStatus({ type: 'error', message: `Error: ${error.message}` })
        } finally {
            setLoading(false)
        }
    }

    const exportCSV = async () => {
        try {
            const response = await axios.get(`${API_BASE}/export/csv`, { responseType: 'blob' })
            const url = window.URL.createObjectURL(new Blob([response.data]))
            const link = document.createElement('a')
            link.href = url
            link.setAttribute('download', `export_${new Date().toISOString().split('T')[0]}.csv`)
            document.body.appendChild(link)
            link.click()
            link.remove()
            setStatus({ type: 'success', message: 'Export downloaded!' })
        } catch (error) {
            setStatus({ type: 'error', message: `Export failed: ${error.message}` })
        }
    }

    const exportJSON = async () => {
        try {
            const response = await axios.get(`${API_BASE}/export/json`, { responseType: 'blob' })
            const url = window.URL.createObjectURL(new Blob([response.data]))
            const link = document.createElement('a')
            link.href = url
            link.setAttribute('download', `export_${new Date().toISOString().split('T')[0]}.json`)
            document.body.appendChild(link)
            link.click()
            link.remove()
            setStatus({ type: 'success', message: 'Export downloaded!' })
        } catch (error) {
            setStatus({ type: 'error', message: `Export failed: ${error.message}` })
        }
    }

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <h2 className="text-xl font-semibold text-gray-900">Reports</h2>
                <div className="flex gap-2">
                    <button onClick={exportCSV} className="px-3 py-2 bg-green-600 text-white rounded hover:bg-green-700 text-sm">
                        Export CSV
                    </button>
                    <button onClick={exportJSON} className="px-3 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm">
                        Export JSON
                    </button>
                </div>
            </div>

            {/* Date Range Selection */}
            <div className="bg-white p-4 rounded-lg shadow">
                <div className="flex gap-4 items-end flex-wrap">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Date Range</label>
                        <select
                            value={dateRange}
                            onChange={(e) => setDateRange(e.target.value)}
                            className="px-3 py-2 border border-gray-300 rounded-md"
                        >
                            <option value="week">Last 7 Days</option>
                            <option value="month">Last 30 Days</option>
                            <option value="quarter">Last 90 Days</option>
                            <option value="year">Last Year</option>
                            <option value="custom">Custom Range</option>
                        </select>
                    </div>
                    {dateRange === 'custom' && (
                        <>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Start Date</label>
                                <input
                                    type="date"
                                    value={startDate}
                                    onChange={(e) => setStartDate(e.target.value)}
                                    className="px-3 py-2 border border-gray-300 rounded-md"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">End Date</label>
                                <input
                                    type="date"
                                    value={endDate}
                                    onChange={(e) => setEndDate(e.target.value)}
                                    className="px-3 py-2 border border-gray-300 rounded-md"
                                />
                            </div>
                        </>
                    )}
                    <button
                        onClick={fetchReport}
                        disabled={loading}
                        className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:opacity-50"
                    >
                        {loading ? 'Loading...' : 'Generate Report'}
                    </button>
                </div>
            </div>

            {/* Report Data */}
            {reportData && (
                <div className="bg-white p-6 rounded-lg shadow">
                    <h3 className="text-lg font-semibold mb-4">Report Summary</h3>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div className="p-4 bg-gray-50 rounded-lg">
                            <p className="text-sm text-gray-500">Total Habits</p>
                            <p className="text-2xl font-bold">{reportData.total_habits || 0}</p>
                        </div>
                        <div className="p-4 bg-gray-50 rounded-lg">
                            <p className="text-sm text-gray-500">Completions</p>
                            <p className="text-2xl font-bold">{reportData.total_completions || 0}</p>
                        </div>
                        <div className="p-4 bg-gray-50 rounded-lg">
                            <p className="text-sm text-gray-500">Completion Rate</p>
                            <p className="text-2xl font-bold">{((reportData.completion_rate || 0) * 100).toFixed(1)}%</p>
                        </div>
                        <div className="p-4 bg-gray-50 rounded-lg">
                            <p className="text-sm text-gray-500">XP Earned</p>
                            <p className="text-2xl font-bold">{reportData.xp_earned || 0}</p>
                        </div>
                    </div>
                </div>
            )}

            {!reportData && (
                <div className="bg-white p-8 rounded-lg shadow text-center text-gray-500">
                    Select a date range and click "Generate Report" to view your data.
                </div>
            )}
        </div>
    )
}

// Settings View
function SettingsView({ setStatus }) {
    const [settings, setSettings] = useState({
        theme: 'light',
        notifications: true,
        quiet_hours_start: '22:00',
        quiet_hours_end: '07:00',
        timezone: 'UTC'
    })
    const [loading, setLoading] = useState(false)

    const fetchSettings = async () => {
        setLoading(true)
        try {
            const response = await axios.get(`${API_BASE}/user/settings`)
            setSettings({ ...settings, ...response.data })
        } catch (error) {
            // Use defaults if endpoint doesn't exist
            setStatus({ type: 'info', message: 'Using default settings' })
        } finally {
            setLoading(false)
        }
    }

    const saveSettings = async () => {
        try {
            await axios.post(`${API_BASE}/user/settings`, settings)
            setStatus({ type: 'success', message: 'Settings saved!' })
        } catch (error) {
            setStatus({ type: 'error', message: `Error saving: ${error.message}` })
        }
    }

    useEffect(() => {
        fetchSettings()
    }, [])

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <h2 className="text-xl font-semibold text-gray-900">Settings</h2>
                <button onClick={saveSettings} className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700">
                    Save Settings
                </button>
            </div>

            {/* Appearance */}
            <div className="bg-white p-6 rounded-lg shadow">
                <h3 className="text-lg font-semibold mb-4">Appearance</h3>
                <div className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Theme</label>
                        <select
                            value={settings.theme}
                            onChange={(e) => setSettings({ ...settings, theme: e.target.value })}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md"
                        >
                            <option value="light">Light</option>
                            <option value="dark">Dark</option>
                            <option value="auto">Auto (System)</option>
                        </select>
                    </div>
                </div>
            </div>

            {/* Notifications */}
            <div className="bg-white p-6 rounded-lg shadow">
                <h3 className="text-lg font-semibold mb-4">Notifications</h3>
                <div className="space-y-4">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="font-medium">Enable Notifications</p>
                            <p className="text-sm text-gray-500">Receive reminders for habits and tasks</p>
                        </div>
                        <button
                            onClick={() => setSettings({ ...settings, notifications: !settings.notifications })}
                            className={`relative inline-flex h-6 w-11 items-center rounded-full ${settings.notifications ? 'bg-primary-600' : 'bg-gray-200'
                                }`}
                        >
                            <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition ${settings.notifications ? 'translate-x-6' : 'translate-x-1'
                                }`} />
                        </button>
                    </div>

                    {settings.notifications && (
                        <div className="grid grid-cols-2 gap-4 pt-4 border-t">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Quiet Hours Start</label>
                                <input
                                    type="time"
                                    value={settings.quiet_hours_start}
                                    onChange={(e) => setSettings({ ...settings, quiet_hours_start: e.target.value })}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Quiet Hours End</label>
                                <input
                                    type="time"
                                    value={settings.quiet_hours_end}
                                    onChange={(e) => setSettings({ ...settings, quiet_hours_end: e.target.value })}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                                />
                            </div>
                        </div>
                    )}
                </div>
            </div>

            {/* Data & Privacy */}
            <div className="bg-white p-6 rounded-lg shadow">
                <h3 className="text-lg font-semibold mb-4">Data & Privacy</h3>
                <div className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Timezone</label>
                        <select
                            value={settings.timezone}
                            onChange={(e) => setSettings({ ...settings, timezone: e.target.value })}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md"
                        >
                            <option value="UTC">UTC</option>
                            <option value="US/Eastern">US Eastern</option>
                            <option value="US/Pacific">US Pacific</option>
                            <option value="Europe/London">Europe/London</option>
                            <option value="Europe/Paris">Europe/Paris</option>
                            <option value="Asia/Tokyo">Asia/Tokyo</option>
                        </select>
                    </div>
                    <div className="pt-4 border-t">
                        <button
                            onClick={() => setStatus({ type: 'info', message: 'Export feature available in Reports tab' })}
                            className="px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200"
                        >
                            Export All Data
                        </button>
                    </div>
                </div>
            </div>

            {/* About */}
            <div className="bg-white p-6 rounded-lg shadow">
                <h3 className="text-lg font-semibold mb-4">About</h3>
                <div className="text-sm text-gray-500 space-y-1">
                    <p><strong>Veryfyn</strong> - Personal Tracking System</p>
                    <p>Version: 2.0.0</p>
                    <p>Architecture: React + FastAPI (Phase 13)</p>
                </div>
            </div>
        </div>
    )
}

export default App
