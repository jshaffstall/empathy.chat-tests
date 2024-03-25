# empathy.chat tests

Testing app for [https://github.com/hugetim/empathy.chat](https://github.com/hugetim/empathy.chat)

## Cloning this app into Anvil

The app in this repository is built with [Anvil](https://anvil.works?utm_source=github:app_README), the framework for building web apps with nothing but Python. You can clone this app into your own Anvil account to test (and modify).

First, fork this repository to your own GitHub user account. Click on the top right of this repo to fork it to your own account.

### Syncing your fork to the Anvil Editor

Then go to the [Anvil Editor](https://anvil.works/build?utm_source=github:app_README) and click on “Clone from GitHub” (underneath the “Blank App” option):

Enter the URL of your forked GitHub repository. If you're not yet logged in, choose "GitHub credentials" as the authentication method and click "Connect to GitHub".

Finally, click "Clone App".

The app will then be in your Anvil account, ready for you to work with.

## Setting up your cloned Anvil app for testing

Next, **before you run the tests app**:
1. Set the value of the 'admin_email' [secret](https://anvil.works/docs/security/encrypting-secret-data#configuration) in your Anvil version of the [empathy.chat app](https://github.com/hugetim/empathy.chat) to an email address you want to use for the admin account (if you haven't already done this).
2. Turning to your Anvil version of this app (empathy.chat tests), set the values of the 'test_user2_email' and 'test_user3_email' [secrets](https://anvil.works/docs/security/encrypting-secret-data#configuration) to two other email addresses you control.
3. Add your Anvil version of the empathy.chat app as a [dependency](https://anvil.works/docs/deployment-new-ide/dependencies) of your empathy.chat-tests app, giving it the package name 'empathy_chat'.

Now you should be ready to run this app and use it for testing.

Find the "Run" button at the top-right of the Anvil editor:

<img src="https://anvil.works/docs/img/run-button-new-ide.png"/>
