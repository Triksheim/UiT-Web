CREATE DEFINER = CURRENT_USER TRIGGER `myDb`.`comments_BEFORE_DELETE` BEFORE DELETE ON `comments` FOR EACH ROW
BEGIN
	INSERT INTO deleted_comments 
	(commentID, text, time, users_username, content_contentID)
	VALUES (old.commentID, old.text, old.time, old.users_username, old.content_contentID);
END;
