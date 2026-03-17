"""
Form Input Components - Consistent Input Styles

Phase 12: UI/UX Redesign - Component Layer

Provides reusable form input components with consistent styling,
validation states, and accessibility features.

Usage:
    from tracking_app.design.components.inputs import (
        render_text_input,
        render_select_input,
        render_checkbox,
        render_textarea,
    )
    
    # Text input
    name = render_text_input(
        label="Habit Name",
        key="habit_name",
        placeholder="Enter habit name",
        required=True
    )
"""

import streamlit as st
from typing import Optional, List, Any, Literal, Callable
from ...design.tokens import COLORS, RADIUS, SPACING

InputSize = Literal["sm", "md", "lg"]
InputVariant = Literal["default", "success", "warning", "error"]


def render_text_input(
    label: str,
    key: str,
    placeholder: Optional[str] = None,
    default: Optional[str] = None,
    help_text: Optional[str] = None,
    required: bool = False,
    disabled: bool = False,
    variant: InputVariant = "default",
    size: InputSize = "md",
    autocomplete: Optional[str] = None,
    on_change: Optional[Callable] = None,
    args: Optional[tuple] = None,
    kwargs: Optional[dict] = None,
) -> Optional[str]:
    """
    Render a styled text input field.
    
    Args:
        label: Input label
        key: Unique Streamlit key
        placeholder: Placeholder text
        default: Default value
        help_text: Help text below input
        required: Whether field is required
        disabled: Whether input is disabled
        variant: Visual variant (success, warning, error)
        size: Input size
        autocomplete: HTML autocomplete attribute
        on_change: Change handler callback
        args: Arguments for on_change
        kwargs: Keyword arguments for on_change
    
    Returns:
        Current input value
    
    Example:
        >>> name = render_text_input(
        ...     label="Habit Name",
        ...     key="habit_name",
        ...     placeholder="e.g., Morning Exercise",
        ...     required=True,
        ...     help_text="Choose a specific, actionable habit"
        ... )
    """
    
    required_marker = " <span style='color: var(--error);'>*</span>" if required else ""
    
    # Variant border colors
    variant_colors = {
        "default": "var(--border)",
        "success": "var(--success)",
        "warning": "var(--warning)",
        "error": "var(--error)",
    }
    border_color = variant_colors.get(variant, variant_colors["default"])
    
    # Size-based styling
    font_size = {"sm": "0.875rem", "md": "1rem", "lg": "1.125rem"}.get(size, "1rem")
    padding = {"sm": "0.5rem 0.75rem", "md": "0.75rem 1rem", "lg": "1rem 1.25rem"}.get(size, "0.75rem 1rem")
    
    value = st.text_input(
        label=f"{label}{required_marker}",
        key=key,
        placeholder=placeholder,
        value=default,
        help=help_text,
        disabled=disabled,
        on_change=on_change,
        args=args or (),
        kwargs=kwargs or {},
        autocomplete=autocomplete,
    )
    
    # Apply variant-specific styling
    if variant != "default":
        st.markdown(f"""
        <style>
        #{key} input {{
            border-color: {border_color} !important;
            box-shadow: 0 0 0 1px {border_color} !important;
        }}
        #{key} input:focus {{
            border-color: {border_color} !important;
            box-shadow: 0 0 0 3px {border_color}20 !important;
        }}
        </style>
        """, unsafe_allow_html=True)
    
    return value


def render_number_input(
    label: str,
    key: str,
    min_value: Optional[float] = None,
    max_value: Optional[float] = None,
    value: Optional[float] = 0.0,
    step: float = 1.0,
    placeholder: Optional[str] = None,
    help_text: Optional[str] = None,
    required: bool = False,
    disabled: bool = False,
    variant: InputVariant = "default",
    size: InputSize = "md",
    on_change: Optional[Callable] = None,
    args: Optional[tuple] = None,
    kwargs: Optional[dict] = None,
) -> Optional[float]:
    """
    Render a styled number input field.
    
    Args:
        label: Input label
        key: Unique Streamlit key
        min_value: Minimum allowed value
        max_value: Maximum allowed value
        value: Default value
        step: Increment step
        placeholder: Placeholder text
        help_text: Help text
        required: Whether field is required
        disabled: Whether input is disabled
        variant: Visual variant
        size: Input size
        on_change: Change handler
    
    Returns:
        Current input value
    
    Example:
        >>> streak_freezes = render_number_input(
        ...     label="Streak Freezes",
        ...     key="streak_freezes",
        ...     min_value=0,
        ...     max_value=10,
        ...     value=3,
        ...     step=1,
        ...     help_text="Number of streak freezes available"
        ... )
    """
    
    required_marker = " <span style='color: var(--error);'>*</span>" if required else ""
    
    value = st.number_input(
        label=f"{label}{required_marker}",
        key=key,
        min_value=min_value,
        max_value=max_value,
        value=value,
        step=step,
        placeholder=placeholder,
        help=help_text,
        disabled=disabled,
        on_change=on_change,
        args=args or (),
        kwargs=kwargs or {},
    )
    
    return value


def render_select_input(
    label: str,
    key: str,
    options: List[Any],
    default: Optional[Any] = None,
    placeholder: Optional[str] = None,
    help_text: Optional[str] = None,
    required: bool = False,
    disabled: bool = False,
    variant: InputVariant = "default",
    size: InputSize = "md",
    format_func: Optional[Callable] = None,
    on_change: Optional[Callable] = None,
    args: Optional[tuple] = None,
    kwargs: Optional[dict] = None,
) -> Optional[Any]:
    """
    Render a styled select dropdown.
    
    Args:
        label: Input label
        key: Unique Streamlit key
        options: List of options
        default: Default selected value
        placeholder: Placeholder text
        help_text: Help text below input
        required: Whether field is required
        disabled: Whether input is disabled
        variant: Visual variant
        size: Input size
        format_func: Function to format option labels
        on_change: Change handler
    
    Returns:
        Selected value
    
    Example:
        >>> priority = render_select_input(
        ...     label="Priority",
        ...     key="task_priority",
        ...     options=["Low", "Medium", "High"],
        ...     default="Medium",
        ...     help_text="Task priority level"
        ... )
    """
    
    required_marker = " <span style='color: var(--error);'>*</span>" if required else ""
    
    value = st.selectbox(
        label=f"{label}{required_marker}",
        key=key,
        options=options,
        index=options.index(default) if default in options else 0,
        placeholder=placeholder,
        help=help_text,
        disabled=disabled,
        format_func=format_func,
        on_change=on_change,
        args=args or (),
        kwargs=kwargs or {},
    )
    
    return value


def render_multiselect(
    label: str,
    key: str,
    options: List[Any],
    default: Optional[List[Any]] = None,
    placeholder: Optional[str] = None,
    help_text: Optional[str] = None,
    required: bool = False,
    disabled: bool = False,
    variant: InputVariant = "default",
    max_selections: Optional[int] = None,
    on_change: Optional[Callable] = None,
    args: Optional[tuple] = None,
    kwargs: Optional[dict] = None,
) -> Optional[List[Any]]:
    """
    Render a styled multi-select dropdown.
    
    Args:
        label: Input label
        key: Unique Streamlit key
        options: List of options
        default: Default selected values
        placeholder: Placeholder text
        help_text: Help text
        required: Whether field is required
        disabled: Whether input is disabled
        variant: Visual variant
        max_selections: Maximum number of selections
        on_change: Change handler
    
    Returns:
        List of selected values
    
    Example:
        >>> categories = render_multiselect(
        ...     label="Categories",
        ...     key="habit_categories",
        ...     options=["Health", "Productivity", "Learning", "Relationships"],
        ...     default=["Health"],
        ...     max_selections=3,
        ...     help_text="Select up to 3 categories"
        ... )
    """
    
    required_marker = " <span style='color: var(--error);'>*</span>" if required else ""
    
    value = st.multiselect(
        label=f"{label}{required_marker}",
        key=key,
        options=options,
        default=default or [],
        placeholder=placeholder,
        help=help_text,
        disabled=disabled,
        max_selections=max_selections,
        on_change=on_change,
        args=args or (),
        kwargs=kwargs or {},
    )
    
    return value


def render_checkbox(
    label: str,
    key: str,
    default: bool = False,
    help_text: Optional[str] = None,
    disabled: bool = False,
    on_change: Optional[Callable] = None,
    args: Optional[tuple] = None,
    kwargs: Optional[dict] = None,
) -> bool:
    """
    Render a styled checkbox.
    
    Args:
        label: Checkbox label
        key: Unique Streamlit key
        default: Default checked state
        help_text: Help text
        disabled: Whether checkbox is disabled
        on_change: Change handler
    
    Returns:
        Current checked state
    
    Example:
        >>> enabled = render_checkbox(
        ...     label="Enable daily reminders",
        ...     key="daily_reminders",
        ...     default=True,
        ...     help_text="Receive notifications every day"
        ... )
    """
    
    value = st.checkbox(
        label=label,
        key=key,
        value=default,
        help=help_text,
        disabled=disabled,
        on_change=on_change,
        args=args or (),
        kwargs=kwargs or {},
    )
    
    return value


def render_toggle(
    label: str,
    key: str,
    default: bool = False,
    help_text: Optional[str] = None,
    disabled: bool = False,
    on_change: Optional[Callable] = None,
    args: Optional[tuple] = None,
    kwargs: Optional[dict] = None,
) -> bool:
    """
    Render a styled toggle switch.
    
    Args:
        label: Toggle label
        key: Unique Streamlit key
        default: Default state
        help_text: Help text
        disabled: Whether toggle is disabled
        on_change: Change handler
    
    Returns:
        Current toggle state
    
    Example:
        >>> dark_mode = render_toggle(
        ...     label="Dark Mode",
        ...     key="dark_mode_toggle",
        ...     default=True,
        ...     help_text="Enable dark theme"
        ... )
    """
    
    # Streamlit doesn't have native toggle, using checkbox styled as toggle
    value = st.checkbox(
        label=label,
        key=key,
        value=default,
        help=help_text,
        disabled=disabled,
        on_change=on_change,
        args=args or (),
        kwargs=kwargs or {},
    )
    
    return value


def render_textarea(
    label: str,
    key: str,
    placeholder: Optional[str] = None,
    default: Optional[str] = None,
    help_text: Optional[str] = None,
    required: bool = False,
    disabled: bool = False,
    variant: InputVariant = "default",
    rows: int = 4,
    max_length: Optional[int] = None,
    on_change: Optional[Callable] = None,
    args: Optional[tuple] = None,
    kwargs: Optional[dict] = None,
) -> Optional[str]:
    """
    Render a styled textarea.
    
    Args:
        label: Input label
        key: Unique Streamlit key
        placeholder: Placeholder text
        default: Default value
        help_text: Help text
        required: Whether field is required
        disabled: Whether input is disabled
        variant: Visual variant
        rows: Number of visible rows
        max_length: Maximum character count
        on_change: Change handler
    
    Returns:
        Current textarea value
    
    Example:
        >>> notes = render_textarea(
        ...     label="Notes",
        ...     key="habit_notes",
        ...     placeholder="Write your notes here...",
        ...     rows=5,
        ...     max_length=500,
        ...     help_text="Optional notes about your habit"
        ... )
    """
    
    required_marker = " <span style='color: var(--error);'>*</span>" if required else ""
    
    value = st.text_area(
        label=f"{label}{required_marker}",
        key=key,
        placeholder=placeholder,
        value=default,
        help=help_text,
        disabled=disabled,
        height=rows * 24 if rows else None,
        max_chars=max_length,
        on_change=on_change,
        args=args or (),
        kwargs=kwargs or {},
    )
    
    # Character count display
    if max_length and value:
        remaining = max_length - len(value)
        st.caption(f"{len(value)}/{max_length} characters ({remaining} remaining)")
    
    return value


def render_radio_buttons(
    label: str,
    key: str,
    options: List[Any],
    default: Optional[Any] = None,
    help_text: Optional[str] = None,
    required: bool = False,
    disabled: bool = False,
    horizontal: bool = False,
    on_change: Optional[Callable] = None,
    args: Optional[tuple] = None,
    kwargs: Optional[dict] = None,
) -> Optional[Any]:
    """
    Render styled radio buttons.
    
    Args:
        label: Group label
        key: Unique Streamlit key
        options: List of options
        default: Default selected value
        help_text: Help text
        required: Whether selection is required
        disabled: Whether radio buttons are disabled
        horizontal: Whether to display horizontally
        on_change: Change handler
    
    Returns:
        Selected value
    
    Example:
        >>> frequency = render_radio_buttons(
        ...     label="Frequency",
        ...     key="habit_frequency",
        ...     options=["Daily", "Weekly", "Monthly"],
        ...     default="Daily",
        ...     horizontal=True
        ... )
    """
    
    required_marker = " <span style='color: var(--error);'>*</span>" if required else ""
    
    value = st.radio(
        label=f"{label}{required_marker}",
        key=key,
        options=options,
        index=options.index(default) if default in options else 0,
        help=help_text,
        disabled=disabled,
        horizontal=horizontal,
        on_change=on_change,
        args=args or (),
        kwargs=kwargs or {},
    )
    
    return value


def render_slider(
    label: str,
    key: str,
    min_value: float = 0.0,
    max_value: float = 100.0,
    value: Optional[float] = None,
    step: float = 1.0,
    format_func: Optional[str] = None,
    help_text: Optional[str] = None,
    disabled: bool = False,
    on_change: Optional[Callable] = None,
    args: Optional[tuple] = None,
    kwargs: Optional[dict] = None,
) -> Optional[float]:
    """
    Render a styled slider.
    
    Args:
        label: Slider label
        key: Unique Streamlit key
        min_value: Minimum value
        max_value: Maximum value
        value: Default value
        step: Increment step
        format_func: Format string for value display
        help_text: Help text
        disabled: Whether slider is disabled
        on_change: Change handler
    
    Returns:
        Current slider value
    
    Example:
        >>> difficulty = render_slider(
        ...     label="Difficulty Level",
        ...     key="habit_difficulty",
        ...     min_value=1,
        ...     max_value=10,
        ...     value=5,
        ...     step=1,
        ...     help_text="How challenging is this habit?"
        ... )
    """
    
    value = st.slider(
        label=label,
        key=key,
        min_value=min_value,
        max_value=max_value,
        value=value if value is not None else (min_value + max_value) / 2,
        step=step,
        format=format_func,
        help=help_text,
        disabled=disabled,
        on_change=on_change,
        args=args or (),
        kwargs=kwargs or {},
    )
    
    return value


def render_date_input(
    label: str,
    key: str,
    value: Optional[Any] = None,
    min_value: Optional[Any] = None,
    max_value: Optional[Any] = None,
    help_text: Optional[str] = None,
    required: bool = False,
    disabled: bool = False,
    on_change: Optional[Callable] = None,
    args: Optional[tuple] = None,
    kwargs: Optional[dict] = None,
) -> Optional[Any]:
    """
    Render a styled date picker.
    
    Args:
        label: Input label
        key: Unique Streamlit key
        value: Default date value
        min_value: Minimum allowed date
        max_value: Maximum allowed date
        help_text: Help text
        required: Whether field is required
        disabled: Whether input is disabled
        on_change: Change handler
    
    Returns:
        Selected date
    
    Example:
        >>> deadline = render_date_input(
        ...     label="Goal Deadline",
        ...     key="goal_deadline",
        ...     min_value=datetime.today(),
        ...     help_text="When do you want to achieve this goal?"
        ... )
    """
    
    required_marker = " <span style='color: var(--error);'>*</span>" if required else ""
    
    value = st.date_input(
        label=f"{label}{required_marker}",
        key=key,
        value=value,
        min_value=min_value,
        max_value=max_value,
        help=help_text,
        disabled=disabled,
        on_change=on_change,
        args=args or (),
        kwargs=kwargs or {},
    )
    
    return value


def render_file_uploader(
    label: str,
    key: str,
    type: Optional[List[str]] = None,
    accept_multiple_files: bool = False,
    help_text: Optional[str] = None,
    disabled: bool = False,
    on_change: Optional[Callable] = None,
    args: Optional[tuple] = None,
    kwargs: Optional[dict] = None,
):
    """
    Render a styled file uploader.
    
    Args:
        label: Uploader label
        key: Unique Streamlit key
        type: Allowed file types (e.g., ["csv", "xlsx"])
        accept_multiple_files: Whether multiple files allowed
        help_text: Help text
        disabled: Whether uploader is disabled
        on_change: Change handler
    
    Returns:
        Uploaded file(s)
    
    Example:
        >>> uploaded = render_file_uploader(
        ...     label="Upload Data",
        ...     key="data_upload",
        ...     type=["csv", "json"],
        ...     accept_multiple_files=False,
        ...     help_text="Supported formats: CSV, JSON"
        ... )
    """
    
    value = st.file_uploader(
        label=label,
        key=key,
        type=type,
        accept_multiple_files=accept_multiple_files,
        help=help_text,
        disabled=disabled,
        on_change=on_change,
        args=args or (),
        kwargs=kwargs or {},
    )
    
    return value


def render_form_input_group(
    inputs: List[dict],
    submit_label: str = "Submit",
    submit_key: str = "form_submit",
    on_submit: Optional[Callable] = None,
    clear_on_submit: bool = False,
):
    """
    Render a group of form inputs within a form.
    
    Args:
        inputs: List of input configurations
        submit_label: Submit button label
        submit_key: Submit button key
        on_submit: Form submit handler
        clear_on_submit: Whether to clear form on submit
    
    Example:
        >>> render_form_input_group([
        ...     {"type": "text", "label": "Name", "key": "name"},
        ...     {"type": "email", "label": "Email", "key": "email"},
        ... ], submit_label="Save")
    """
    
    with st.form(key=f"form_{submit_key}"):
        for input_config in inputs:
            input_type = input_config.get("type", "text")
            
            if input_type == "text":
                render_text_input(
                    label=input_config.get("label", "Input"),
                    key=input_config.get("key", "input"),
                    placeholder=input_config.get("placeholder"),
                    required=input_config.get("required", False),
                    help_text=input_config.get("help"),
                )
            elif input_type == "textarea":
                render_textarea(
                    label=input_config.get("label", "Input"),
                    key=input_config.get("key", "input"),
                    rows=input_config.get("rows", 4),
                )
            elif input_type == "select":
                render_select_input(
                    label=input_config.get("label", "Input"),
                    key=input_config.get("key", "input"),
                    options=input_config.get("options", []),
                )
            elif input_type == "checkbox":
                render_checkbox(
                    label=input_config.get("label", "Checkbox"),
                    key=input_config.get("key", "input"),
                )
        
        submitted = st.form_submit_button(
            label=submit_label,
            on_click=on_submit,
        )
        
        if submitted and clear_on_submit:
            st.rerun()


__all__ = [
    "render_text_input",
    "render_number_input",
    "render_select_input",
    "render_multiselect",
    "render_checkbox",
    "render_toggle",
    "render_textarea",
    "render_radio_buttons",
    "render_slider",
    "render_date_input",
    "render_file_uploader",
    "render_form_input_group",
    "InputSize",
    "InputVariant",
]
