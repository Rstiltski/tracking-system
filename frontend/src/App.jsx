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

export default App
