To run, navigate to the root directory in the command line and execute "flask run".

Navigate to localhost:5000 to interact with the system (tested on Firefox 71.0 and Chrome 78.0, Windows 10).

Logging in is simplified to involve entering a user ID. All IDs in the range 0-999 are valid.
If you wish to access and modify a "blank" user profile you may use IDs 0, 5, 12, 13, 14, 16, 19, or 20, all of which
are verified to be uninstantiated (haven't made any recommendations).

Features:
- Users can do a basic pattern search against the set of books.
- Users can update their ratings, or make new ratings, for any book appearing on the screen. The list of books is then
dynamically updated (including recalculating book recommendations if a recommended book is rated).
- Users can view, modify, and delete their old ratings.
- Users can see the overall rating dynamically updated in the search tab ("Find & Rate Books").