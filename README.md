# Chatbot Oral English Teacher

This is a tool for students to upload their homework like audio recordings througth social media (Line), when audio be uploaded on the platform, AI by Azure will analyse the recording and give intial feedback based on the crietia of their pronounciation. For teachers, they have the access to the backend page to review all the recording sent from students.


## Introduction

Allows a teacher to view audio recordings sent by students via LINE

### Use case for students:

1. Select the question they would like to upload
![images](https://github.com/andy0427s/linebotTeacher/blob/main/imgs/Picture1.png)
![images](https://github.com/andy0427s/linebotTeacher/blob/main/imgs/Picture2.png)

2. Start the recording

![images](https://github.com/andy0427s/linebotTeacher/blob/main/imgs/Picture3.png)

3. The system receives the recording from students and give feedback

![images](https://github.com/andy0427s/linebotTeacher/blob/main/imgs/Picture4.png)

### Use case for teachers

1. In the remove/edit page, they can do the CRUD operations to the students homework if they think the autograde given by the system should be revaluated.

![images](https://github.com/andy0427s/linebotTeacher/blob/main/imgs/Picture5.png)

2. In the review page, they can review student's homework manually.
 
![images](https://github.com/andy0427s/linebotTeacher/blob/main/imgs/Picture6.png)


## Documentation

See the official API documentation for more information.

- English: https://developers.line.biz/en/docs/messaging-api/overview/
- Japanese: https://developers.line.biz/ja/docs/messaging-api/overview/


## Requirements

This library requires Python 3.6 or later.


## Flowchart

![image](https://github.com/andy0427s/linebotTeacher/blob/main/imgs/Screen%20Shot%202022-10-09%20at%203.52.30%20PM.png)


## Modules

This project contains the following modules:

 * line-bot-api-client: API client library for the Messaging API
 * line-bot-model: Model classes for the Messaging API



## Help and media
FAQ: https://developers.line.biz/en/faq/

Community Q&A: https://www.line-community.me/questions

News: https://developers.line.biz/en/news/

Twitter: [@LINE_DEV](https://twitter.com/LINE_DEV)


## Versioning

This project respects semantic versioning.

See http://semver.org/.


## Contributing

Please check [CONTRIBUTING](CONTRIBUTING.md) before making a contribution.


## License

    Copyright (C) 2016 LINE Corp.

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
