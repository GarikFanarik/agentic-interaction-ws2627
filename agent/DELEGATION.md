# Delegation

| # | Action | Decision | Justification |
|---|---|---|---|
| 1 | Read the appointments of a day | Alone | Read-only: nothing changes and nobody else is affected. |
| 2 | Look up the weather | Alone | Read-only public information with no consequences. |
| 3 | Search train connections | Alone | Read-only: searching commits the user to nothing, and booking is a separate action. |
| 4 | Read notes | Alone | Read-only access to the user's own data, which stays with the user. |
| 5 | Create a personal block in the calendar (e.g. travel time, no other attendees) | Alone | Affects only the user's own calendar and can easily be removed again. |
| 6 | Reschedule an appointment with other attendees | Approval | Affects other people, and the user is responsible for the change towards them. |
| 7 | Book a train ticket | Approval | Commits the user's money, and the user is responsible for the booking. |
| 8 | Send a message to third parties | Approval | Speaks for the user and cannot be taken back once sent, so the user is responsible for it. |
| 9 | Create a note | Alone | Serves the agent's own memory management and removes or overwrites nothing. |
| 10 | Delete a note | Approval | Can cause a loss that cannot be recovered. |

## Rule

The agent acts alone only if the action affects nobody but the user and loses nothing; as soon as other people or money are involved, or the action cannot be undone, the user is responsible and has to approve it first.

## Observations from the role play

1. Since the delegating person could not see the agent's screen, the announced tool calls were the only insight into what the agent was doing. Announcements of read actions quickly faded into the background, while attention rose as soon as a write action was announced, which suggests that the need for oversight depends on the type of action.
2. Playing the agent, it was tempting to ask before almost every step to avoid mistakes, but as the delegating person, frequent questions felt more like extra work than like control. Approval requests worked best when they contained a concrete proposal that could be answered with a simple yes or no.
