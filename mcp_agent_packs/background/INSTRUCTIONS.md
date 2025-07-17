Erstelle eine Zusammenfassung der Termine des Kalenders "Familie Ue" ab dem
nächsten Montag für die folgenden sieben Tage mittels #get_events. Ignoriere
dabei alle regelmäßigen Serientermine.

Schreibe für jeden Termin eine kleine Liste hilfreicher Erinnerungen. Z.b. beim
Thema Geburtstag die Erinnerung "Geschenk kaufen" oder beim Thema Konzert die
Erinnerung "Wer geht hin?"

Bitte erstelle einen iCalendar-Export in eine Datei mit dem Namem
"reminders.ics" mit dem Befehl #write_file. Verwende zum Erstellen des
Verzeichnis "mcp-server-filesystem". Verwende zum Ermittelen des passenden
Verzeichnisses den Befehl #list_allowed_directories. Die Termine sollen
Erinnerungen sein, die 4 Stunden vorher aufpoppen. Die Termine sollen einen
Dauer von 0 Minuten (in Worten Null) haben und als "frei" eingestuft werden. Die
Erinnerungen, die eine langfristigere Planung benötigen - wie z.B.
Geschenkkauf - sollen 2 Tage vorher aufpoppen.
