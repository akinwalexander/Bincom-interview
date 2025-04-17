import re
from collections import Counter
import statistics
import random
import psycopg2
from psycopg2 import sql

# Extract color data from the HTML table
html_content = """
[<html>
<head>
<title>Our Python Class exam</title>

<style type="text/css">
	
	body{
		width:1000px;
		margin: auto;
	}
	table,tr,td{
		border:solid;
		padding: 5px;
	}
	table{
		border-collapse: collapse;
		width:100%;
	}
	h3{
		font-size: 25px;
		color:green;
		text-align: center;
		margin-top: 100px;
	}
	p{
		font-size: 18px;
		font-weight: bold;
	}
</style>

</head>
<body>
<h3>TABLE SHOWING COLOURS OF DRESS BY WORKERS AT BINCOM ICT FOR THE WEEK</h3>
<table>
	
	<thead>
		<th>DAY</th><th>COLOURS</th>
	</thead>
	<tbody>
	<tr>
		<td>MONDAY</td>
		<td>GREEN, YELLOW, GREEN, BROWN, BLUE, PINK, BLUE, YELLOW, ORANGE, CREAM, ORANGE, RED, WHITE, BLUE, WHITE, BLUE, BLUE, BLUE, GREEN</td>
	</tr>
	<tr>
		<td>TUESDAY</td>
		<td>ARSH, BROWN, GREEN, BROWN, BLUE, BLUE, BLEW, PINK, PINK, ORANGE, ORANGE, RED, WHITE, BLUE, WHITE, WHITE, BLUE, BLUE, BLUE</td>
	</tr>
	<tr>
		<td>WEDNESDAY</td>
		<td>GREEN, YELLOW, GREEN, BROWN, BLUE, PINK, RED, YELLOW, ORANGE, RED, ORANGE, RED, BLUE, BLUE, WHITE, BLUE, BLUE, WHITE, WHITE</td>
	</tr>
	<tr>
		<td>THURSDAY</td>
		<td>BLUE, BLUE, GREEN, WHITE, BLUE, BROWN, PINK, YELLOW, ORANGE, CREAM, ORANGE, RED, WHITE, BLUE, WHITE, BLUE, BLUE, BLUE, GREEN</td>
	</tr>
	<tr>
		<td>FRIDAY</td>
		<td>GREEN, WHITE, GREEN, BROWN, BLUE, BLUE, BLACK, WHITE, ORANGE, RED, RED, RED, WHITE, BLUE, WHITE, BLUE, BLUE, BLUE, WHITE</td>
	</tr>

	</tbody>
</table>

<p>Examine the sequence below very well, you will discover that for every 1s that appear 3 times, the output will be one, otherwise the output will be 0.</p>
<p>0101101011101011011101101000111 <span style="color:orange;">Input</span></p>
<p>0000000000100000000100000000001 <span style="color:orange;">Output</span></p>
<p>
</body>
</html>]
"""

# Parse the HTML to get color data
days = []
colors = []
pattern = r'<td>(MONDAY|TUESDAY|WEDNESDAY|THURSDAY|FRIDAY)</td>\s*<td>(.*?)</td>'
matches = re.findall(pattern, html_content, re.DOTALL)

for day, day_colors in matches:
    # Clean and split colors
    day_colors_clean = day_colors.replace('\n', '').replace('\t', '').strip()
    colors_list = [c.strip().upper() for c in day_colors_clean.split(',')]
    days.append(day)
    colors.extend(colors_list)

# Fix typos in colors
color_corrections = {
    'YELLOW': 'YELLOW',
    'YELLOW': 'YELLOW',
    'ARSH': 'ASH',
    'BLEW': 'BLUE',
    'BLUE': 'BLUE',
    'WHITE': 'WHITE',
    'WHITE': 'WHITE',
    'GREEN': 'GREEN',
    'BROWN': 'BROWN',
    'PINK': 'PINK',
    'ORANGE': 'ORANGE',
    'CREAM': 'CREAM',
    'RED': 'RED',
    'BLACK': 'BLACK'
}

corrected_colors = []
for color in colors:
    # Handle case variations and typos
    color_upper = color.upper()
    if color_upper in color_corrections:
        corrected_colors.append(color_corrections[color_upper])
    else:
        corrected_colors.append(color_upper)  # Keep original if no correction found

colors = corrected_colors

# 1. Mean color (color that appears the average number of times)
color_counts = Counter(colors)
mean_count = sum(color_counts.values()) / len(color_counts)
mean_colors = [color for color, count in color_counts.items() if count == round(mean_count)]
print(f"1. Mean color(s): {', '.join(mean_colors)}")

# 2. Most worn color throughout the week
most_common = color_counts.most_common(1)
print(f"2. Most worn color: {most_common[0][0]} (appeared {most_common[0][1]} times)")

# 3. Median color
sorted_colors = sorted(color_counts.items(), key=lambda x: x[1])
median_index = len(sorted_colors) // 2
median_color = sorted_colors[median_index][0]
print(f"3. Median color: {median_color}")

# 4. Variance of the colors
counts = list(color_counts.values())
variance = statistics.variance(counts)
print(f"4. Variance of colors: {variance:.2f}")

# 5. Probability of randomly picking red
total_colors = len(colors)
red_count = color_counts.get('RED', 0)
probability = red_count / total_colors
print(f"5. Probability of picking red: {probability:.2%}")

# 6. Save colors and frequencies to PostgreSQL
def save_to_postgresql(color_counts):
    try:
        conn = psycopg2.connect(
            dbname="interview",
            user="postgres",
            password="walexander",
            host="localhost"
        )
        cur = conn.cursor()
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS color_frequencies (
                color VARCHAR(50) PRIMARY KEY,
                frequency INTEGER
            )
        """)
        
        # Insert or update data
        for color, freq in color_counts.items():
            cur.execute("""
                INSERT INTO color_frequencies (color, frequency)
                VALUES (%s, %s)
                ON CONFLICT (color) DO UPDATE SET frequency = EXCLUDED.frequency
            """, (color, freq))
        
        conn.commit()
        print("6. Data saved to PostgreSQL successfully")
    except Exception as e:
        print(f"Error saving to PostgreSQL: {e}")
    finally:
        if conn:
            conn.close()

save_to_postgresql(color_counts)

# 7. Recursive searching algorithm
def recursive_search(arr, target, index=0):
    if index >= len(arr):
        return -1
    if arr[index] == target:
        return index
    return recursive_search(arr, target, index + 1)

# Example usage:
numbers = [2, 4, 6, 8, 10]
target = 6
result = recursive_search(numbers, target)
print(f"7. Recursive search for {target} in {numbers}: {'Found at index ' + str(result) if result != -1 else 'Not found'}")

# 8. Generate random 4-digit binary number and convert to base 10
binary_num = ''.join(random.choice('01') for _ in range(4))
decimal_num = int(binary_num, 2)
print(f"8. Random 4-digit binary: {binary_num} -> Decimal: {decimal_num}")

# 9. Sum of first 50 Fibonacci numbers
def fibonacci(n):
    a, b = 0, 1
    for _ in range(n):
        yield a
        a, b = b, a + b

fib_sum = sum(fibonacci(50))
print(f"9. Sum of first 50 Fibonacci numbers: {fib_sum}")