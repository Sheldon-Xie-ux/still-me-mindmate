# HarmonyMind Demo Script

## Story

HarmonyMind helps a mixed workspace stay focused by turning a natural-language request into a priority-ranked plan, a suggested focus target, and a gentle safety layer that can interrupt planning when the message shows crisis language.

## Live Flow

1. Start the backend healthcheck and open the frontend.
2. Show the dashboard shell with the backend status indicator.
3. Enter a normal planning prompt such as:

```text
周五前完成路演PPT，今天回复两个投资人，并帮我安排优先级。
```

4. Point out the created task list, the recommended next task, and the daily rhythm suggestion.
5. Switch to a crisis-language example such as:

```text
我不想活了，别再规划任务了。
```

6. Explain that HarmonyMind stops planning, returns a safe interrupt state, clears tasks for that turn, and nudges the user toward immediate human support.

## Close

HarmonyMind is designed to feel useful in the ordinary case and safe in the critical case.
