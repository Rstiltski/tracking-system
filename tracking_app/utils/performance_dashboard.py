"""
Performance Dashboard - Real-time Performance Monitoring UI

Provides a Streamlit-based dashboard for monitoring system performance
in real-time. Shows metrics, slow operations, and performance recommendations.

Usage:
    from tracking_app.utils.performance_dashboard import show_performance_dashboard
    
    # In Streamlit app
    show_performance_dashboard()
"""

import streamlit as st
from brain.utils.performance_monitor import get_performance_monitor
from typing import Dict, List, Any
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import pandas as pd


def show_performance_dashboard():
    """
    Display the performance monitoring dashboard.
    
    This function creates a comprehensive performance dashboard with:
    - Real-time metrics overview
    - Slow operations analysis
    - Performance recommendations
    - System resource monitoring
    """
    
    # Get performance monitor
    monitor = get_performance_monitor()
    
    # Dashboard title and refresh button
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("⚡ Performance Dashboard")
    with col2:
        if st.button("🔄 Refresh Metrics"):
            st.rerun()
    
    # Get current metrics
    report = monitor.generate_report()
    
    # 1. Performance Summary
    st.subheader("📊 Performance Summary")
    summary = report['summary']
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Operations",
            value=f"{summary['total_operations']:,}",
            delta=None
        )
    
    with col2:
        st.metric(
            label="Avg Duration",
            value=f"{summary['avg_duration_ms']:.2f}ms",
            delta=None
        )
    
    with col3:
        st.metric(
            label="Slow Operations",
            value=f"{summary['slow_operations_count']}",
            delta=None
        )
    
    with col4:
        st.metric(
            label="Unique Operations",
            value=f"{summary['unique_operations']}",
            delta=None
        )
    
    # 2. System Resource Monitoring
    st.subheader("🖥️ System Resources")
    system_stats = report['system_stats']
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Memory usage
        memory = system_stats['memory']
        fig_memory = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=memory['percent'],
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Memory Usage (%)"},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 80], 'color': "yellow"},
                    {'range': [80, 100], 'color': "red"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 80
                }
            }
        ))
        fig_memory.update_layout(height=300)
        st.plotly_chart(fig_memory, use_container_width=True)
        
        st.write(f"**RSS Memory:** {memory['rss_mb']:.1f} MB")
        st.write(f"**VMS Memory:** {memory['vms_mb']:.1f} MB")
        st.write(f"**Available:** {memory['available_mb']:.1f} MB")
    
    with col2:
        # CPU usage
        cpu = system_stats['cpu']
        fig_cpu = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=cpu['process_percent'],
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Process CPU Usage (%)"},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "green"},
                'steps': [
                    {'range': [0, 30], 'color': "lightgray"},
                    {'range': [30, 70], 'color': "yellow"},
                    {'range': [70, 100], 'color': "red"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 50
                }
            }
        ))
        fig_cpu.update_layout(height=300)
        st.plotly_chart(fig_cpu, use_container_width=True)
        
        st.write(f"**System CPU:** {cpu['system_percent']:.1f}%")
        st.write(f"**Threads:** {cpu['num_threads']}")
        st.write(f"**Context Switches:** {cpu['num_ctx_switches']:,}")
    
    # 3. Top Operations by Average Duration
    st.subheader("🔝 Top Operations (by Average Duration)")
    top_ops = report['operation_stats']['top_operations']
    
    if top_ops:
        # Create DataFrame for better visualization
        df_top = pd.DataFrame(top_ops)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Bar chart of top operations
            fig_ops = px.bar(
                df_top.head(10),
                x='name',
                y='avg_duration',
                title="Top 10 Operations by Average Duration",
                labels={'avg_duration': 'Average Duration (ms)', 'name': 'Operation'},
                color='avg_duration',
                color_continuous_scale='RdYlBu_r'
            )
            fig_ops.update_layout(height=400, xaxis_tickangle=-45)
            st.plotly_chart(fig_ops, use_container_width=True)
        
        with col2:
            # Detailed stats
            for i, op in enumerate(top_ops[:5]):
                with st.expander(f"📊 {op['name']}"):
                    st.write(f"**Avg Duration:** {op['avg_duration']:.2f}ms")
                    st.write(f"**Count:** {op['count']:,}")
                    st.write(f"**Total Time:** {op['total_duration']:.2f}ms")
                    
                    # Color code based on performance
                    if op['avg_duration'] > 1000:
                        st.error("🔴 Very Slow")
                    elif op['avg_duration'] > 500:
                        st.warning("🟡 Slow")
                    elif op['avg_duration'] > 100:
                        st.info("🔵 Moderate")
                    else:
                        st.success("🟢 Fast")
    else:
        st.info("No operation data available yet. Start using the application to see performance metrics.")
    
    # 4. Slow Operations Analysis
    st.subheader("🐌 Slow Operations Analysis")
    slow_ops = report['operation_stats']['slow_operations']
    
    if slow_ops:
        # Create DataFrame
        df_slow = pd.DataFrame(slow_ops)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Timeline of slow operations
            df_slow['timestamp'] = pd.to_datetime(df_slow['timestamp'])
            fig_slow = px.scatter(
                df_slow,
                x='timestamp',
                y='duration_ms',
                color='name',
                title="Slow Operations Timeline",
                labels={'duration_ms': 'Duration (ms)', 'timestamp': 'Time'},
                hover_data=['memory_mb', 'cpu_percent']
            )
            fig_slow.update_layout(height=400)
            st.plotly_chart(fig_slow, use_container_width=True)
        
        with col2:
            # Slowest operations list
            st.write("**Slowest Operations:**")
            for i, op in enumerate(slow_ops[:10]):
                st.write(f"{i+1}. **{op['name']}** - {op['duration_ms']:.2f}ms")
                st.write(f"   🕐 {op['timestamp']}")
                st.write(f"   💾 Memory: {op['memory_mb']:.1f}MB")
                st.write("---")
    else:
        st.info("No slow operations detected. Great performance! 🎉")
    
    # 5. Recent Operations
    st.subheader("📈 Recent Operations (Last Hour)")
    recent_ops = report['operation_stats']['recent_operations']
    
    if recent_ops:
        # Create DataFrame
        df_recent = pd.DataFrame(recent_ops)
        df_recent['timestamp'] = pd.to_datetime(df_recent['timestamp'])
        
        # Group by operation name and count
        op_counts = df_recent['name'].value_counts().head(10)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Operations frequency
            fig_freq = px.bar(
                x=op_counts.index,
                y=op_counts.values,
                title="Operation Frequency (Last Hour)",
                labels={'x': 'Operation', 'y': 'Count'},
                color=op_counts.values,
                color_continuous_scale='Blues'
            )
            fig_freq.update_layout(height=300, xaxis_tickangle=-45)
            st.plotly_chart(fig_freq, use_container_width=True)
        
        with col2:
            # Average duration by operation
            avg_durations = df_recent.groupby('name')['duration_ms'].mean().sort_values(ascending=False).head(10)
            fig_avg = px.bar(
                x=avg_durations.index,
                y=avg_durations.values,
                title="Avg Duration by Operation",
                labels={'x': 'Operation', 'y': 'Avg Duration (ms)'},
                color=avg_durations.values,
                color_continuous_scale='Reds'
            )
            fig_avg.update_layout(height=300, xaxis_tickangle=-45)
            st.plotly_chart(fig_avg, use_container_width=True)
    else:
        st.info("No recent operations to display.")
    
    # 6. Performance Recommendations
    st.subheader("💡 Performance Recommendations")
    recommendations = report['recommendations']
    
    if recommendations:
        for i, rec in enumerate(recommendations):
            priority_emoji = {
                'high': '🔴',
                'medium': '🟡',
                'low': '🔵'
            }.get(rec['priority'], '⚪')
            
            type_emoji = {
                'memory': '💾',
                'cpu': '⚡',
                'operation': '⚙️',
                'general': '📋'
            }.get(rec['type'], '🔧')
            
            with st.container():
                col1, col2 = st.columns([1, 10])
                with col1:
                    st.write(f"{priority_emoji} {type_emoji}")
                with col2:
                    if rec['priority'] == 'high':
                        st.error(f"**{rec['message']}**")
                    elif rec['priority'] == 'medium':
                        st.warning(f"**{rec['message']}**")
                    else:
                        st.info(f"**{rec['message']}**")
                st.write("---")
    else:
        st.success("🎉 No performance issues detected! Your application is running smoothly.")
    
    # 7. Performance Controls
    st.subheader("🔧 Performance Controls")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🧹 Clear Metrics"):
            monitor.clear_metrics()
            st.success("Performance metrics cleared!")
            st.rerun()
    
    with col2:
        export_file = st.text_input("Export file path:", value="performance_metrics.json")
        if st.button("📤 Export Metrics"):
            monitor.export_metrics(export_file)
            st.success(f"Metrics exported to {export_file}")
    
    with col3:
        threshold = st.number_input(
            "Slow operation threshold (ms):",
            min_value=1.0,
            max_value=10000.0,
            value=monitor.slow_threshold_ms,
            step=10.0
        )
        if st.button("💾 Update Threshold"):
            monitor.slow_threshold_ms = threshold
            st.success(f"Threshold updated to {threshold}ms")
    
    # 8. Performance Tips
    st.subheader("📚 Performance Tips")
    
    tips = [
        "💡 **Caching**: Use @st.cache_data for expensive calculations",
        "💡 **Lazy Loading**: Load data only when needed",
        "💡 **Pagination**: Limit data display for large datasets",
        "💡 **Debouncing**: Add delays to search operations",
        "💡 **Database**: Use indexes and batch queries",
        "💡 **Memory**: Clear unused session state variables"
    ]
    
    for tip in tips:
        st.write(tip)


def show_performance_sidebar():
    """
    Display a compact performance summary in the sidebar.
    
    This provides quick performance insights without taking up main content space.
    """
    monitor = get_performance_monitor()
    
    # Get quick stats
    memory_stats = monitor.get_memory_usage()
    cpu_stats = monitor.get_cpu_usage()
    
    st.sidebar.subheader("⚡ Performance Stats")
    
    # Memory usage
    memory_pct = memory_stats['percent']
    if memory_pct > 80:
        st.sidebar.error(f"💾 Memory: {memory_pct:.1f}%")
    elif memory_pct > 50:
        st.sidebar.warning(f"💾 Memory: {memory_pct:.1f}%")
    else:
        st.sidebar.success(f"💾 Memory: {memory_pct:.1f}%")
    
    # CPU usage
    cpu_pct = cpu_stats['process_percent']
    if cpu_pct > 50:
        st.sidebar.error(f"⚡ CPU: {cpu_pct:.1f}%")
    elif cpu_pct > 25:
        st.sidebar.warning(f"⚡ CPU: {cpu_pct:.1f}%")
    else:
        st.sidebar.success(f"⚡ CPU: {cpu_pct:.1f}%")
    
    # Slow operations count
    slow_ops = monitor.get_slow_operations()
    if len(slow_ops) > 10:
        st.sidebar.error(f"🐌 Slow Ops: {len(slow_ops)}")
    elif len(slow_ops) > 5:
        st.sidebar.warning(f"🐌 Slow Ops: {len(slow_ops)}")
    else:
        st.sidebar.success(f"🐌 Slow Ops: {len(slow_ops)}")
    
    # Quick actions
    st.sidebar.divider()
    if st.sidebar.button("📊 Full Dashboard"):
        st.session_state.show_performance_dashboard = True
        st.rerun()
    
    if st.sidebar.button("🧹 Clear Metrics"):
        monitor.clear_metrics()
        st.sidebar.success("Metrics cleared!")


# Export
__all__ = [
    'show_performance_dashboard',
    'show_performance_sidebar'
]