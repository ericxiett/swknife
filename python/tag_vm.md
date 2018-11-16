# TAG TARGETED VMS

1. Setup parser as well as logging configurations
  * parser configurations
  * logger format
2. Read vm list from a excel doc
  * check input values before tagging
3. Add tag one by one
  * for speed up, list concise representation of vm (detailed=False)
  * list all existing tags for a given server and add tag if it's not already present
  * recursively retrieving all servers to avoid **default limit**
4. Exception handling
