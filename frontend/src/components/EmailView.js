import React from 'react';
import utf8 from 'utf8';
import quotedPrintable from 'quoted-printable';
import {
  encode, decode, trim,
  isBase64, isUrlSafeBase64
} from 'url-safe-base64'
import xss from 'xss'

const DEFAULT_PAGE_SIZE = 10;

class EmailView extends React.Component {

  constructor(props) {
    super(props);
    this.state = {listOfHtml : [],
    html : '',
    emailList: [],
    commonHeadersList: [],
    curr_index : 0,
    nextPageToken : '',
    pageSize : DEFAULT_PAGE_SIZE}
    this.moveNext = this.moveNext.bind(this);
    this.fetchDataV2 = this.fetchDataV2.bind(this)
    this.selectEmail = this.selectEmail.bind(this);
    this.loadMore = this.loadMore.bind(this);
  }

  componentDidMount(){
   this.fetchDataV2();
   this.startFetching10More(this);
  }

  startFetching10More(referenceToThis) {
    let interval = setInterval(function(){
      // method to be executed;
       console.log(referenceToThis.state.nextPageToken);
       if (referenceToThis.state.nextPageToken !== 'NULL' &&
           referenceToThis.state.emailList !== undefined &&
           referenceToThis.state.pageSize !== undefined &&
           referenceToThis.state.emailList.length < referenceToThis.state.pageSize) {
         referenceToThis.moveNext();
       } else {
         clearInterval(interval);
       }
     }, 5000);
  }

 fetchDataV2() {
   let str = '';
   let newList = [];
   fetch("http://localhost:4444/api/v2/emails/search?fromAddress=no-reply@sns.amazonaws.com&numOfEmails=5&labelIds=Label_5098114589143438238")
   .then((resp) => {
    return resp.json();
    })
    .then((data) => {
      this.setStateVariables(data);
    }).catch(error => {
      console.log('HERE!!');
      console.log(error);
      this.setState({'nextPageToken' : 'NULL'});
    });
  }


  setStateVariables(data) {
    let currNextPageToken = 'NULL';
    if (data.pageToken !== 'NULL') {
         currNextPageToken = data.pageToken;
    }
    console.log('---------------------------------------------');
    console.log('IN SET STATE VARIABLES: ' + currNextPageToken);
    //console.log(data.pageToken)
    data = data.emails;
    let currEmailList = this.state.emailList;
    let currCommonHeadersList = this.state.commonHeadersList;
    try{
      for (let i in data) {
        let awsData = trim(data[i]['payload']['body']['data'] + '==');
        let urlSafeBase64AwsData = decode(awsData);
        let base64decodedAwsData = atob(urlSafeBase64AwsData);
        let utf8decodedAwsData;
        try {
          utf8decodedAwsData = JSON.parse(base64decodedAwsData);
        } catch(error1) {
            console.log('error1');
            let otherNotificationType = decode(base64decodedAwsData).split('%2D%2D')[0].split('If you wish to stop receiving notifications from this topic, please click or visit the link below to unsubscribe:')[0];
          console.log(otherNotificationType.substring(0, otherNotificationType.length - 5));
            try {
              utf8decodedAwsData = JSON.parse(otherNotificationType.substring(0, otherNotificationType.length - 5));
            } catch (error2) {
              console.log('error2');
              console.log(error2);
            }
        }
            let jsonParsedEmail;
            try {
              jsonParsedEmail = JSON.parse(utf8decodedAwsData['Message']);
            } catch (error3) {
              console.log('error3');
              try {
              jsonParsedEmail = JSON.parse(utf8decodedAwsData['content']);
            } catch (error4) {
              console.log('error4');
              jsonParsedEmail = utf8decodedAwsData;
              }
            }
            try {
              jsonParsedEmail['mail']['commonHeaders']['messageId'] = jsonParsedEmail['mail']['commonHeaders']['messageId']+ (this.state.commonHeadersList.length + i + 1);
              currCommonHeadersList.push(jsonParsedEmail['mail']['commonHeaders']);
              currEmailList.push(jsonParsedEmail);
              }
            catch(error) {
              try {
                console.log('error5');
                jsonParsedEmail['mail']['messageId'] = jsonParsedEmail['mail']['messageId'] +
                  (this.state.commonHeadersList.length + i + 1);
                currCommonHeadersList.push({
                  'from': jsonParsedEmail['mail']['destination'],
                  'messageId' : jsonParsedEmail['mail']['messageId']
                });
                currEmailList.push(jsonParsedEmail);
              }
              catch (error) {
                console.log('error6');
                console.log(jsonParsedEmail);
                console.log('PASS NOW');
              }
              // This could be "Type" : "Notification"

              // console.log('PASS THAT EMAIL');
            }
          }
        }
      catch(error) {
        console.log('IN THE BAD ZONE!')
        console.log(error);
      }
    this.setState({
      emailList: currEmailList,
      commonHeadersList : currCommonHeadersList,
      nextPageToken : currNextPageToken});
  }

  moveNext() {
    let str = '';
    let newList = [];
    let isEnd = false;
    fetch("http://localhost:4444/api/v2/emails/search?fromAddress=no-reply@sns.amazonaws.com&numOfEmails=15&pageToken="+this.state.nextPageToken+"&labelIds=Label_5098114589143438238")
    .then((resp) => {
     return resp.json();
     })
     .then((data) => {
       this.setStateVariables(data);
     }).catch((error) => {
       isEnd = true;
     });
    }

  selectEmail(event) {
    console.log(this.state.emailList);
      let currEmailJSON = this.state.emailList[parseInt(event.target.name)];
      let currContent = currEmailJSON['content'];
      console.log(currContent);
      let emailList = [];
      let regex = /Content[-+]Type:/g;
      if (regex.test(currContent)) {
        emailList = currContent.split(regex);
        if (emailList > 1) {
          emailList.splice(0,1);
        }
      }
      try {
        currContent = emailList[emailList.length-1];
        currContent = quotedPrintable.decode(currContent);
        // console.log(currContent);
      } catch(error) {
        console.log(error);
      }
      console.log('SIZE OF LIST: ' + emailList.length);
      this.setState({html : currContent});
    }

  loadMore() {
    this.state.pageSize += 10;
    this.startFetching10More(this);
  }

  render() {
    const insertableHTML = this.state.html
    const commonHeadersList = this.state.commonHeadersList.map((header, index) => {
      return  <div>
        <button style={{width:'500px'}}
                className="listItem"
                name={index}
                key={header.messageId}
                onClick={this.selectEmail}>
            {decode(header.from[0].replace(/[<>]/g,'')).replaceAll('=', '.')}<br />
            {header.subject}
        </button>
      </div>
      }
    );
    return (
      <div>
        {commonHeadersList}
        <div style={{margin:'1vw'}}>
        {this.state.nextPageToken !== 'NULL' &&
         this.state.emailList.length < this.state.pageSize ?
            'Loading More...' :
            <button onClick={this.loadMore}>Load More</button>}
        </div>
        <div dangerouslySetInnerHTML={{__html:insertableHTML}}></div>

      </div>
    );
  }
}

export default EmailView;
