# import fbchat
# from getpass import getpass
# input()
# username = str("rodrigo-cosendey@hotmail.com")
# client = fbchat.Client(username, getpass())
# no_of_friends = int(1)
# name = str("p1p2testy")
# friends = client.getUsers(name)  # return a list of names
# friend = friends[0]
# msg = str("mexican")
# sent = client.send(friend.uid, msg)
# if sent:
# 		print("Message sent successfully!")

#restaurant chat 
# <!-- Messenger Chat plugin Code -->
#     <div id="fb-root"></div>

#     <!-- Your Chat plugin code -->
#     <div id="fb-customer-chat" class="fb-customerchat">
#     </div>

#     <script>
#       var chatbox = document.getElementById('fb-customer-chat');
#       chatbox.setAttribute("page_id", "100386825619946");
#       chatbox.setAttribute("attribution", "biz_inbox");
#       window.fbAsyncInit = function() {
#         FB.init({
#           xfbml            : true,
#           version          : 'v11.0'
#         });
#       };

#       (function(d, s, id) {
#         var js, fjs = d.getElementsByTagName(s)[0];
#         if (d.getElementById(id)) return;
#         js = d.createElement(s); js.id = id;
#         js.src = 'https://connect.facebook.net/en_US/sdk/xfbml.customerchat.js';
#         fjs.parentNode.insertBefore(js, fjs);
#       }(document, 'script', 'facebook-jssdk'));
#     </script>