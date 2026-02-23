from flask import Flask, render_template_string
import csv

app = Flask(__name__)

# Upgraded HTML Template with Tailwind CSS and FontAwesome Icons
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="2"> 
    <title>Proctoring AI Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
</head>
<body class="bg-slate-50 text-slate-800 font-sans antialiased p-6 md:p-10">
    <div class="max-w-6xl mx-auto">

        <div class="flex items-center justify-between bg-white p-6 rounded-xl shadow-sm mb-6 border border-slate-200">
            <div class="flex items-center gap-4">
                <div class="bg-indigo-600 p-4 rounded-xl text-white shadow-md">
                    <i class="fa-solid fa-shield-halved text-3xl"></i>
                </div>
                <div>
                    <h1 class="text-2xl font-bold text-slate-900 tracking-tight">AI Proctoring Command Center</h1>
                    <p class="text-sm text-slate-500 font-medium">Real-time Exam Surveillance Session</p>
                </div>
            </div>

            <div class="flex items-center gap-2 bg-red-50 px-4 py-2 rounded-full border border-red-100 shadow-sm">
                <span class="relative flex h-3 w-3">
                  <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
                  <span class="relative inline-flex rounded-full h-3 w-3 bg-red-600"></span>
                </span>
                <span class="text-sm font-bold text-red-600 uppercase tracking-wider">Live Monitoring</span>
            </div>
        </div>

        <div class="bg-white rounded-xl shadow-sm overflow-hidden border border-slate-200">
            <div class="px-6 py-4 border-b border-slate-200 bg-slate-50 flex justify-between items-center">
                <h2 class="text-lg font-bold text-slate-800"><i class="fa-solid fa-list-ul mr-2 text-indigo-500"></i> Recent Violations Log</h2>
                <span class="text-xs font-semibold text-slate-500 uppercase tracking-wider">Auto-updating...</span>
            </div>

            <div class="overflow-x-auto">
                <table class="w-full text-left border-collapse">
                    <thead>
                        <tr class="bg-white text-slate-500 text-sm border-b border-slate-200 uppercase tracking-wider">
                            <th class="py-4 px-6 font-semibold w-48">Timestamp</th>
                            <th class="py-4 px-6 font-semibold w-56">Violation Type</th>
                            <th class="py-4 px-6 font-semibold">Flag Details</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-slate-100">
                        {% if logs %}
                            {% for row in logs %}
                            <tr class="hover:bg-slate-50 transition-colors duration-150 ease-in-out">
                                <td class="py-4 px-6 text-sm font-medium text-slate-600 whitespace-nowrap">
                                    <i class="fa-regular fa-clock mr-2 text-slate-400"></i>{{ row[0] }}
                                </td>
                                <td class="py-4 px-6">
                                    {% if row[1] == 'Audio' %}
                                        <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-amber-100 text-amber-700 border border-amber-200">
                                            <i class="fa-solid fa-microphone-lines"></i> Audio
                                        </span>
                                    {% elif row[1] == 'Environment' %}
                                        <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-slate-200 text-slate-700 border border-slate-300">
                                            <i class="fa-solid fa-desktop"></i> Environment
                                        </span>
                                    {% elif row[1] == 'Face Detection' %}
                                        <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-purple-100 text-purple-700 border border-purple-200">
                                            <i class="fa-solid fa-users"></i> Face Detection
                                        </span>
                                    {% elif row[1] == 'Gaze Tracking' %}
                                        <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-blue-100 text-blue-700 border border-blue-200">
                                            <i class="fa-regular fa-eye"></i> Gaze Tracking
                                        </span>
                                    {% else %}
                                        <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-emerald-100 text-emerald-700 border border-emerald-200">
                                            <i class="fa-solid fa-check"></i> {{ row[1] }}
                                        </span>
                                    {% endif %}
                                </td>
                                <td class="py-4 px-6 text-sm text-slate-700 font-medium">{{ row[2] }}</td>
                            </tr>
                            {% endfor %}
                        {% else %}
                            <tr>
                                <td colspan="3" class="py-12 text-center text-slate-500">
                                    <div class="flex flex-col items-center justify-center">
                                        <div class="bg-emerald-50 p-4 rounded-full mb-3">
                                            <i class="fa-solid fa-shield-check text-4xl text-emerald-500"></i>
                                        </div>
                                        <p class="text-emerald-700 font-bold text-lg">Exam session is secure.</p>
                                        <p class="text-sm text-slate-500 mt-1">No violations have been recorded yet.</p>
                                    </div>
                                </td>
                            </tr>
                        {% endif %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</body>
</html>
"""


@app.route('/')
def index():
    logs = []
    try:
        # Open and read the CSV file generated by monitor.py
        with open('exam_log.csv', 'r') as f:
            reader = csv.reader(f)
            header = next(reader, None)  # Skip the header row
            if header:
                logs = list(reader)[::-1]  # Reverse the list so newest logs are at the top
    except FileNotFoundError:
        pass  # If the exam hasn't started and no file exists, just return an empty table

    return render_template_string(HTML_TEMPLATE, logs=logs)


if __name__ == '__main__':
    print("Starting Premium Proctor Dashboard...")
    app.run(debug=True, port=5000)