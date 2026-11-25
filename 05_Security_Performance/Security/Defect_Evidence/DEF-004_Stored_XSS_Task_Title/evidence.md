# DEF-004 - Stored XSS: task title rendered unescaped

| Field | Value |
|---|---|
| Severity | Critical |
| Found by | Alia (TC-SEC-009) |
| Related test cases | TC-SEC-009 |
| Status | Open - **REPRODUCED** on 2026-11-25 13:09:04 |
| Environment | Python 3.14.7, Flask 3.0.3, SQLite (fresh temp DB), Windows 11, Chrome headless (Selenium) |
| Reproduced by | `07_Test_Management/Defect_Evidence/reproduce_defects.py` (def004) |

## Expected
Title shown as plain text (HTML-escaped).

## Actual (observed in this run)
The title is rendered with |safe, so the stored <script> runs for every visit to the task list.

## Screenshots
**screenshot_xss_executed.png** - Task list after login: the red banner was created by JavaScript stored in a task title.

![Task list after login: the red banner was created by JavaScript stored in a task title.](screenshot_xss_executed.png)

## Captured request / response trace
```text
# setup: registered 'alice_d4' -> HTTP 201
[1] >>> POST /api/tasks   json={'title': '<script>document.body.insertAdjacentHTML(\'afterbegin\',\'<h1 id=xss style="background:#c00;color:#fff;padding:12px">XSS EXECUTED - injected by task title</h1>\')</script>'}
    <<< HTTP 201
[2] >>> GET /
    <<< HTTP 200
# Payload appears UNESCAPED in the HTML of '/': True
# HTML line: <td class="title-cell"><script>document.body.insertAdjacentHTML('afterbegin','<h1 id=xss style="background:#c00;color:#fff;padding:12px">XSS EXECUTED - injected by task title</h1>')</script></td>
# Browser: element #xss created by the stored script = True
```

## Root cause - faulty source lines (`>>` marks the defect)
```text
app/templates/index.html
     43 |             </td>
>>   44 |             <td class="title-cell">{{ t.title|safe }}</td>
     45 |             <td>{{ t.category or '—' }}</td>
```
