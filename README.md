# Cloudurity Intership Assessments

## Python Test Set - 1

- Create a microblogging site (like twitter) that allows only text posts, with a max character limit of 150 characters.

- Users can create new posts, reply to existing posts and like existing posts.

- The UI can be very minimal to allow posting, replying, liking for authenticated users and viewing only for unauthenticated users.

- The preferred language is Python, though the candidates are free to use any language of their choice.

- Likewise, the candidates are free to use any database of their choice.

- The implementation should be published in GitHub and the link to the GitHub repository should be shared with us.

## Gallery

![image](https://github.com/thetrotfreak/hiss/assets/45330487/e0afb149-8cd7-43c9-af77-591606aa2840)

![image](https://github.com/thetrotfreak/hiss/assets/45330487/6f31e154-ab72-41c0-931d-b63b5a41d3d5)

## Installation

### Ubuntu 22.04.4 LTS
1. Setup a virtual environment
```shell
python3 -m venv venv
```
2. Activate the virtual environment
```shell
source venv/bin/activate
```
> ^For Bash & Bash-like shell
3. Install requirements
```shell
pip install -r requirements.txt
```
4. Install the `.whl` file
```shell
pip install hiss-1.0.0-py3-none-any.whl
```
> ^Check the version number
5. Intialize the sqlite3 database
```shell
flask --app hiss init-db
```
6. Start the development server
```shell
flask --app hiss run --debug
```
