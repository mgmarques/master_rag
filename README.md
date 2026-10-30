# Master RAG: Ultimate Retrieval-Augmented Generation Course


1. Setup and Python installation 
2. Create API keys & set the environment variables 

### [1]-Setup and Python installation

#### macOS
1. **Check if Python is already installed**
   ```sh
   python3 --version
   ```
   If Python is not installed, proceed with the steps below.

2. **Install Homebrew (if not installed)**
   ```sh
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

3. **Install Python**
   ```sh
   brew install python3
   ```

4. **Check Python Version**
   ```sh
   python3 --version
   ```

#### Windows
1. **Download Python** from the official website: [https://www.python.org/downloads/](https://www.python.org/downloads/)

2. **Run the installer** and check the box **"Add Python to PATH"** before proceeding with the installation.

3. **Check Python Version**
   ```sh
   python --version
   ```
---


### [2]-Create API keys & set the environment variables 


#### 2.1 Setting Up OpenAI Secret Key  
1. Create an OpenAI Account[OpenAI's API Keys page](https://platform.openai.com/signup/),
2. Go to [OpenAI's API Keys page](https://platform.openai.com/settings/organization/api-keys),
3. Click **Create new secret key** and copy it, 
4. You will need to add your billing information (MANAGE > Settings > Billing).  


#### 2.2 LangSmith
1. Create a [LangSmith Account](https://smith.langchain.com/),

**2.1 Create a project**
![Create a project](images/1.png)

**2.2 Provide a name**
![Provide a name](images/2.png)

**2.3 Configure Project**
![Configure Project](images/3.png)


#### Set environment variables 

##### macOS & Linux  
You can store the key in your shell configuration file:  

```sh
echo 'export OPENAI_API_KEY="your-secret-key"' >> ~/.bashrc
source ~/.bashrc
````

or add to `.env` file (update the `.env.example` file)

```sh
OPENAI_API_KEY="YOUR_OPENAI_API_KEY_H"
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY="YOUR_LANGSMITH_API_KEY"
LANGSMITH_PROJECT="PROJECT_NAME"

```



