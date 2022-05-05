CREATE DEFINER = CURRENT_USER TRIGGER `myDb`.`comment_BEFORE_DELETE` BEFORE DELETE ON `comment` FOR EACH ROW
BEGIN
	INSERT INTO deleted_comment 
	(commentID, text, time, user_username, content_contentID)
	VALUES (old.commentID, old.text, old.time, old.user_username, old.content_contentID);
END;