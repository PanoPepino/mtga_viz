# MTGMelee scraper notes

This scraper sends the same authenticated round-match request that the browser sends to MTGMelee, then saves a minimal CSV with selected match fields. The two values that usually need manual inspection are the login cookie and the round IDs used by the request. 

## How to inspect your cookie

1. Open MTGMelee in the browser and log in first. The request cookie is easiest to inspect from the browser's developer tools after the session is active.
2. Open Developer Tools with `Cmd + Option + I` on macOS, or `F12` / `Ctrl + Shift + I` on Windows and Linux. 
3. Go to the **Network** tab, then filter to **Fetch/XHR** so the round-loading requests are easier to spot. 
4. Click a round in MTGMelee so the site performs the request that loads round data. 
5. In the request list, click the request related to round matches, then open **Headers**. 
6. Under **Request Headers**, find the line beginning with `Cookie:` and copy the full value. This is the string to paste into the scraper's `COOKIE` variable. 
7. If the `Cookie:` line is difficult to copy, right-click the request and use **Copy as cURL** instead, then extract the cookie from the `-b` or `Cookie:` part. Copy-as-cURL preserves the exact request that worked in the browser. 
8. If the scraper stops working later, inspect the cookie again. Authentication cookies can expire or change when the session changes. 

## How to inspect the round ID

1. Stay in **Network** and trigger the round load again by clicking the desired round. 
2. Open the request that loaded the round data. 
3. Check the **Request URL**. In this workflow, the round ID appears at the end of the path, in a request shaped like `/Match/GetRoundMatches/<round_id>`. 
4. Copy the numeric suffix from that URL and add it to the list used by the scraper. 
5. If several rounds are needed, click each round once and collect the different numeric IDs that appear in the request URL. 
6. If there is any doubt, compare two requests from two different rounds and note which number changes. The changing value is the round ID. 

