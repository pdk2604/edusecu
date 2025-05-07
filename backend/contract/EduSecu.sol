// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract EduSecu {
    struct Document {
        string fullName;
        string docType;
        uint256 timestamp;
        bool isValid;
    }

    mapping(string => Document) private documents;

    function addDocument(string memory hash, string memory fullName, string memory docType) public {
        require(!documents[hash].isValid, "Document already exists");

        documents[hash] = Document({
            fullName: fullName,
            docType: docType,
            timestamp: block.timestamp,
            isValid: true
        });
    }

    function verifyDocument(string memory hash) public view returns (string memory, string memory, uint256, bool) {
        Document memory doc = documents[hash];
        return (doc.fullName, doc.docType, doc.timestamp, doc.isValid);
    }
}
