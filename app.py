import random
import time
from typing import List, Dict, Any

import gradio as gr


# ----------------------------
# QUICKSORT WITH STEP TRACKING
# ----------------------------

def quicksort_with_steps(arr: List[int]) -> Dict[str, Any]:
    # Make a copy so we never mutate original input
    nums = arr[:]

    # Stores every action for visualization
    steps: List[Dict[str, Any]] = []

    # Records a single step into the steps list
    def record_step(left, right, pivot_index, i, j, action):
        steps.append({
            "array": nums[:],      # snapshot of array
            "left": left,          # left boundary of current partition
            "right": right,        # right boundary
            "pivot_index": pivot_index,
            "i": i,                # left pointer index
            "j": j,                # right pointer index
            "description": action   # explanation text
        })

    # ----------------------------------------------------------
    # UPDATED PARTITION FUNCTION AS REQUESTED
    # Pivot = last element in subarray
    # Hoare-style inward pointers (i →, j ←)
    # ----------------------------------------------------------
    def partition(left, right):
        """
        Partition using:
        - pivot = last element
        - left pointer (i) moves right
        - right pointer (j) moves left
        They zero in on each other until they meet/cross.
        """
        pivot_value = nums[right]      # Last element = pivot
        i = left                       # Left pointer starts at left
        j = right - 1                  # Right pointer starts before pivot

        # Log pivot selection
        record_step(left, right, right, i, j,
                    f"Pivot = {pivot_value} at index {right} (last element)")

        while True:

            # Move left pointer right while element < pivot
            while i < right and nums[i] < pivot_value:
                record_step(left, right, right, i, j,
                            f"nums[{i}] = {nums[i]} < pivot → move left pointer right")
                i += 1

            # Move right pointer left while element > pivot
            while j >= left and nums[j] > pivot_value:
                record_step(left, right, right, i, j,
                            f"nums[{j}] = {nums[j]} > pivot → move right pointer left")
                j -= 1

            # Stop when pointers cross
            if i >= j:
                record_step(left, right, right, i, j,
                            "Pointers met/crossed → partition done")
                break

            # Swap values pointed by i and j
            record_step(left, right, right, i, j,
                        f"Swapping nums[{i}] = {nums[i]} and nums[{j}] = {nums[j]}")
            nums[i], nums[j] = nums[j], nums[i]
            record_step(left, right, right, i, j,
                        f"After swap: nums[{i}] = {nums[i]}, nums[{j}] = {nums[j]}")

            # Move inward after swap
            i += 1
            j -= 1

        # After crossing, pivot goes to index i
        record_step(left, right, right, i, right,
                    f"Placing pivot {pivot_value} into index {i}")
        nums[i], nums[right] = nums[right], nums[i]
        record_step(left, right, i, i, right,
                    f"Pivot {pivot_value} placed at index {i}")

        return i

    # ----------------------------------------------------------

    def quicksort(left, right):
        # Base case: no sorting needed
        if left >= right:
            record_step(left, right, -1, -1, -1,
                        f"Subarray [{left},{right}] is size ≤ 1 → done")
            return

        # Log start of quicksort on this subarray
        record_step(left, right, -1, -1, -1,
                    f"Sorting subarray [{left},{right}]")

        # Partition then recurse
        p = partition(left, right)
        quicksort(left, p - 1)
        quicksort(p + 1, right)

    # Start quicksort if array is not empty
    if nums:
        quicksort(0, len(nums) - 1)

    return {"sorted": nums, "steps": steps}


# ----------------------------
# HTML VISUALIZATION (unchanged)
# ----------------------------

def render_step(step: Dict[str, Any]) -> str:
    # Extract everything needed for drawing
    arr = step["array"]
    left = step["left"]
    right = step["right"]
    pivot = step["pivot_index"]
    i = step["i"]
    j = step["j"]
    description = step["description"]

    if not arr:
        return "<p>No data.</p>"

    # Scale bars nicely
    max_val = max(arr)
    max_val = max(max_val, 1)

    # Determine type of step for animations
    desc_lower = description.lower()
    is_swap_pre = "swapping" in desc_lower
    is_swap_post = "after swap" in desc_lower
    is_pivot_event = "pivot" in desc_lower

    # Title
    html = """
    <div style="text-align:center; margin-bottom:8px;">
        <h2 style="margin:0;">Quicksort Step</h2>
    </div>
    """

    # Container for bars
    html += "<div style='display:flex; justify-content:center; align-items:flex-end; gap:14px; margin-bottom:14px;'>"

    # Function to draw ONE bar
    def bar_div(index, value):
        height = (value / max_val) * 260

        # Color choice
        if index == pivot:
            color = "linear-gradient(to top, #f44336, #ff7961)"
        elif index == i:
            color = "linear-gradient(to top, #2e7d32, #81c784)"
        elif index == j:
            color = "linear-gradient(to top, #1565c0, #64b5f6)"
        else:
            color = "linear-gradient(to top, #757575, #e0e0e0)"

        # Glow depending on active pointer / pivot
        border_glow = ""
        if index == i:
            border_glow = "box-shadow: 0 0 12px 3px rgba(0,255,0,0.6);"
        elif index == j:
            border_glow = "box-shadow: 0 0 12px 3px rgba(0,100,255,0.6);"
        elif index == pivot and is_pivot_event:
            border_glow = "box-shadow: 0 0 12px 3px rgba(255,0,0,0.6);"

        # Swap animation scale
        scale = 1.0
        if index in (i, j):
            if is_swap_pre:
                scale = 0.6
            elif is_swap_post:
                scale = 1.18
        elif index == pivot and is_pivot_event:
            scale = 1.12

        return f"""
        <div style="
            width: 48px;
            height: {height}px;
            background: {color};
            border-radius: 8px 8px 0 0;
            display:flex;
            justify-content:center;
            align-items:flex-end;
            font-size:14px;
            font-weight:bold;
            color:black;
            {border_glow}
            transform: scaleY({scale});
            transition: transform 0.35s ease;
        ">{value}</div>
        """

    # If the subarray indices are valid, highlight it
    if 0 <= left <= right < len(arr):
        # prefix
        for idx in range(left):
            html += bar_div(idx, arr[idx])

        # highlighted range
        html += """
        <div style="
            border:2px solid #555;
            border-radius:8px;
            padding:8px;
            display:flex;
            gap:14px;
            background:#fafafa;
        ">
        """
        for idx in range(left, right + 1):
            html += bar_div(idx, arr[idx])
        html += "</div>"

        # suffix
        for idx in range(right + 1, len(arr)):
            html += bar_div(idx, arr[idx])

    else:
        # otherwise draw full array normally
        for idx, val in enumerate(arr):
            html += bar_div(idx, val)

    html += "</div>"

    # For pointer highlight boxes below bars
    cell_width = 48
    cell_gap = 14
    offset_unit = cell_width + cell_gap

    html += "<div style='display:flex; justify-content:center; margin-top:4px;'>"
    html += "<div style='position:relative; display:inline-block; padding:6px 0;'>"

    # Left pointer highlight
    if isinstance(i, int) and 0 <= i < len(arr):
        html += f"""
        <div style="
            position:absolute;
            top:0; left:0;
            width:{cell_width}px;
            height:100%;
            border-radius:6px;
            border:2px solid #2e7d32;
            background:rgba(76,175,80,0.08);
            transform: translateX({i * offset_unit}px);
            transition: transform 0.35s ease;
            z-index:1;
        "></div>
        """

    # Right pointer highlight
    if isinstance(j, int) and 0 <= j < len(arr):
        html += f"""
        <div style="
            position:absolute;
            top:0; left:0;
            width:{cell_width}px;
            height:100%;
            border-radius:6px;
            border:2px solid #1565c0;
            background:rgba(33,150,243,0.08);
            transform: translateX({j * offset_unit}px);
            transition: transform 0.35s ease;
            z-index:2;
        "></div>
        """

    # Draw index numbers
    html += "<div style='position:relative; display:flex;'>"
    for idx in range(len(arr)):
        gap = cell_gap if idx < len(arr) - 1 else 0
        html += f"""
        <div style="
            width:{cell_width}px;
            margin-right:{gap}px;
            text-align:center;
            font-size:16px;
            color:#333;
        ">{idx}</div>
        """
    html += "</div></div></div>"

    # Explanation under graph
    html += f"""
    <div style='text-align:center; margin-top:12px; font-size:18px;'>
        <strong>Explanation:</strong> {description}
    </div>
    """

    return html


# ----------------------------
# INPUT / UI CALLBACKS (unchanged)
# ----------------------------

def parse_user_input(array_text: str, size_text: str):
    """
    Parses either:
    - A manually entered array (comma-separated)
    - Or a requested random array size
    """
    array_text = array_text.strip()
    size_text = size_text.strip()

    # If user manually entered an array
    if array_text:
        try:
            arr = [int(x.strip()) for x in array_text.split(",") if x.strip() != ""]
        except ValueError:
            return None, "Invalid array input. Please enter integers separated by commas."
        if len(arr) > 20:
            return None, "Array must be at most 20 items."
        return arr, ""

    # Otherwise, generate random array
    if not size_text:
        return None, "Enter a size between 1–20 or an array."

    try:
        n = int(size_text)
    except ValueError:
        return None, "Size must be a number."

    if n < 1 or n > 20:
        return None, "Size must be between 1 and 20."

    arr = [random.randint(1, 99) for _ in range(n)]
    return arr, ""


def start_sort(array_text, size_text, steps_state, index_state):
    """
    Triggered when the user presses 'Start Sort'.
    Generates steps, resets slider, loads first frame.
    """
    arr, error = parse_user_input(array_text, size_text)
    if error:
        return (
            "",
            "",
            [],
            0,
            error,
            gr.update(value=0, minimum=0, maximum=1, interactive=False),
        )

    result = quicksort_with_steps(arr)
    steps = result["steps"]

    slider_cfg = gr.update(
        minimum=0,
        maximum=max(0, len(steps) - 1),
        value=0,
        step=1,
        interactive=True,
    )

    return (
        f"Sorted Array: {result['sorted']}",
        render_step(steps[0]),
        steps,
        0,
        "",
        slider_cfg,
    )


def move_step(direction, steps_state, index_state):
    """
    Moves step index left or right by 1 (for Back/Forward buttons).
    """
    steps = steps_state or []
    if not steps:
        return "", index_state, gr.update()

    idx = max(0, min(index_state + direction, len(steps) - 1))
    return render_step(steps[idx]), idx, gr.update(value=idx)


def go_to_step(steps_state, slider_val):
    """
    Jump to any step using slider.
    """
    steps = steps_state or []
    if not steps:
        return "", 0

    idx = int(slider_val)
    idx = max(0, min(idx, len(steps) - 1))
    return render_step(steps[idx]), idx


def auto_play(steps_state, index_state):
    """
    Auto-plays steps from current index to end with a delay.
    """
    steps = steps_state or []
    if not steps:
        yield "", index_state, gr.update()
        return

    idx = index_state
    while idx < len(steps) - 1:
        idx += 1
        yield render_step(steps[idx]), idx, gr.update(value=idx)
        time.sleep(0.6)


def build_interface():
    """
    Builds Gradio interface layout:
    - Input boxes
    - Buttons
    - Visualization window
    - Step slider
    """
    with gr.Blocks(title="Quicksort Visualizer Application") as demo:

        gr.Markdown(
            """
            <h1 style="text-align:center; margin-bottom:-10px;">
                Quicksort Visualizer Application
            </h1>
            <p style="text-align:center; font-size:14px; color:#555;">
                Visualize how Quicksort partitions and sorts an array step-by-step.
            </p>
            """
        )

        steps_state = gr.State([])
        index_state = gr.State(0)

        with gr.Row():
            with gr.Column(scale=3):
                array_text = gr.Textbox(
                    label="Enter your array (optional)",
                    placeholder="Example: 7, 3, 9, 1, 4",
                    lines=4,
                )
            with gr.Column(scale=1):
                size_text = gr.Textbox(
                    label="Choose your input size (1–20)",
                    placeholder="e.g., 10",
                    lines=1,
                )

        error_box = gr.Markdown("")

        with gr.Row():
            start_button = gr.Button("Start Sort", variant="primary")
            back_button = gr.Button("Back")
            forward_button = gr.Button("Forward")
            play_button = gr.Button("Play")

        sorted_output = gr.Textbox(label="Sorted Result", interactive=False)
        visualization = gr.HTML(label="Quicksort Visualization")

        step_slider = gr.Slider(
            label="Step", minimum=0, maximum=1, value=0, step=1, interactive=False
        )

        # Bind button + slider callbacks
        start_button.click(
            start_sort,
            [array_text, size_text, steps_state, index_state],
            [sorted_output, visualization, steps_state, index_state, error_box, step_slider],
        )

        back_button.click(
            lambda steps, idx: move_step(-1, steps, idx),
            [steps_state, index_state],
            [visualization, index_state, step_slider],
        )

        forward_button.click(
            lambda steps, idx: move_step(1, steps, idx),
            [steps_state, index_state],
            [visualization, index_state, step_slider],
        )

        step_slider.change(
            go_to_step,
            [steps_state, step_slider],
            [visualization, index_state],
        )

        play_button.click(
            auto_play,
            [steps_state, index_state],
            [visualization, index_state, step_slider],
        )

    return demo


demo = build_interface()

if __name__ == "__main__":
    demo.launch()
